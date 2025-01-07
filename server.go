package main

import (
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"time"

	_ "github.com/mattn/go-sqlite3" // Или замените на драйвер для вашей БД
)

type Channel struct {
	ChID int    `json:"chid"`
	ChNm string `json:"chnm"`
	MsId int    `json:"msid"`
}

type Message struct {
	ChID int    `json:"chid"`
	MsId int    `json:"msid"`
	Text string `json:"text"`
	DtMs string `json:"dtms"`
	DtCl string `json:"dtcl"`
}

type Response struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

// func main() {
// 	http.HandleFunc("/svmess", handleSVMess)
// 	log.Println("Server is running on port 8080...")
// 	log.Fatal(http.ListenAndServe(":8080", nil))
// }

func handleSVMess(w http.ResponseWriter, r *http.Request) {
	DATABASE, exists := os.LookupEnv("DATABASE")
	if !exists {
		log.Println("Нет DATABASE")
	}

	if r.Method != http.MethodPost {
		log.Println("Invalid request method")
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var msg Message
	if err := json.NewDecoder(r.Body).Decode(&msg); err != nil {
		log.Println("Invalid JSON:", err)
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	db, err := sql.Open("sqlite3", DATABASE)
	if err != nil {
		log.Fatalf("Ошибка подключения к базе данных: %v", err)
	}
	defer db.Close()

	// db, err := openDB()
	// if err != nil {
	// 	http.Error(w, "Database connection error", http.StatusInternalServerError)
	// 	log.Println("Database connection error:", err)
	// 	return
	// }
	// defer db.Close()

	sql := "INSERT INTO mess (chid, msid, text, dtms, dtcl) VALUES ($1, $2, $3, $4, $5)"
	_, err = db.Exec(sql, msg.ChID, msg.MsId, msg.Text, msg.DtMs, msg.DtCl)

	if err != nil {
		response := Response{Success: false, Message: fmt.Sprintf("Insert failed: %v", err)}
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(response)
		log.Println("Insert failed:", err)
		return
	}

	sql2 := "REPLACE INTO mesus (chid, msid, usid) SELECT $1, $2, usid from usch u WHERE u.chid = $3"
	_, err = db.Exec(sql2, msg.ChID, msg.MsId, msg.ChID)

	if err != nil {
		response := Response{Success: false, Message: fmt.Sprintf("Insert failed: %v", err)}
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(response)
		log.Println("Insert failed:", err)
		return
	} else {
		response := Response{Success: true, Message: "Message inserted successfully"}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(response)
	}

	// if err := insertMessage(db, msg); err != nil {
	// 	response := Response{Success: false, Message: fmt.Sprintf("Insert failed: %v", err)}
	// 	w.WriteHeader(http.StatusInternalServerError)
	// 	json.NewEncoder(w).Encode(response)
	// 	log.Println("Insert failed:", err)
	// 	return
	// }

	// response := Response{Success: true, Message: "Message inserted successfully"}
	// w.Header().Set("Content-Type", "application/json")
	// w.WriteHeader(http.StatusOK)
	// json.NewEncoder(w).Encode(response)
}

// Главный обработчик для отображения index.html
func handleFilter(w http.ResponseWriter, r *http.Request, usid int) {
	log.Println("/filter", r.Method, r.RemoteAddr)
	file, err := os.ReadFile("./web/index.html")
	if err != nil {
		file = []byte{}
	}
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.WriteHeader(http.StatusOK)
	w.Write(file)
}

func handleGSFilter(w http.ResponseWriter, r *http.Request, usid int) {
	log.Println("/stfltr", r.Method, r.RemoteAddr)
	// usid := 391497468
	// hash := get_hash(usid)
	DATABASE, exists := os.LookupEnv("DATABASE")
	if !exists {
		log.Println("Нет DATABASE")
	}
	// Настройка соединения с базой данных
	db, err := sql.Open("sqlite3", DATABASE)
	if err != nil {
		log.Fatalf("Ошибка подключения к базе данных: %v", err)
	}
	defer db.Close()

	if r.Method != http.MethodPost {
		log.Println("Запрос фильтра")

		// Выполнение SQL-запроса
		// sql := `SELECT wrkrule FROM usrs WHERE usid = $1;`
		sql := `SELECT '{"name":"' || full_name ||' ('|| username || ')",' || REPLACE (wrkrule, '{"filter"', '"filter"') FROM usrs `
		// wrkrule, err = db.Exec(sql, usid)
		rows, err := db.Query(sql, usid)

		if err != nil {
			http.Error(w, fmt.Sprintf("Ошибка выполнения запроса: %v", err), http.StatusInternalServerError)
			log.Println("Ошибка выполнения запроса: %v", err)
			return
		}
		defer rows.Close()

		var wrkrule string
		count := 0
		for rows.Next() {
			count++
			if count > 1 {
				log.Fatal(errors.New("/stfltr, more than one row wrkrule returned"))
			}
			if err := rows.Scan(&wrkrule); err != nil {
				log.Fatal(err)
			}
		}
		if count == 0 {
			log.Println("/stfltr, no row wrkrule found")
			usid = 0
		}

		log.Println(wrkrule)
		// response := Response{Success: true, Message: wrkrule}
		// w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Content-Type", "text")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, wrkrule)
		// json.NewEncoder(w).Encode(response)
		return
	} else {
		log.Println("Запись фильтра")

		bodyBytes, err := io.ReadAll(r.Body)
		if err != nil {
			log.Fatal("Ошибка чтения Body", err)
		}
		filter := string(bodyBytes)
		// Выполнение SQL-запроса
		sql := `UPDATE usrs SET wrkrule = $1 WHERE usid = $2;`
		_, err = db.Exec(sql, filter, usid)
		if err != nil {
			http.Error(w, fmt.Sprintf("Ошибка выполнения update: %v", err), http.StatusInternalServerError)
			return
		} else {
			response := Response{Success: true, Message: "Filter updated successfully"}
			w.Header().Set("Content-Type", "application/json")
			// w.Header().Set("Content-Type", "text")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)
			// fmt.Fprintf(w, wrkrule)
		}
	}
}

// var flag bool = false

// func authorized1(next func(http.ResponseWriter, *http.Request)) func(http.ResponseWriter, *http.Request) {
// 	return func(w http.ResponseWriter, r *http.Request) {
// 		if !flag {
// 			http.Redirect(w, r, "/login", http.StatusSeeOther)
// 			return
// 		}
// 		next(w, r)
// 	}
// }

func get_user(hash string) int {

	DATABASE, exists := os.LookupEnv("DATABASE")
	if !exists {
		log.Fatalf("Нет DATABASE %v", exists)
		return 0
	}

	// Настройка соединения с базой данных
	db, err := sql.Open("sqlite3", DATABASE)
	if err != nil {
		log.Fatalf("Ошибка подключения к базе данных: %v", err)
		return 0
	}
	defer db.Close()

	sql := `SELECT usid FROM usrs WHERE hash = $1;`
	// wrkrule, err = db.Exec(sql, usid)
	rows, err := db.Query(sql, hash)

	if err != nil {
		log.Fatalf("Ошибка выполнения запроса: %v", err)
		return 0
	}
	defer rows.Close()

	var usid int
	count := 0
	for rows.Next() {
		count++
		if count > 1 {
			log.Fatal(errors.New("get_user, more than one row returned"))
		}
		if err := rows.Scan(&usid); err != nil {
			log.Fatal(err)
		}
	}
	if count == 0 {
		log.Println("get_user, no user found")
		usid = 0
	}
	return usid
}

func get_hash(usid int) (hash string) {

	DATABASE, exists := os.LookupEnv("DATABASE")
	if !exists {
		log.Fatalf("Нет DATABASE %v", exists)
		return "0"
	}

	// Настройка соединения с базой данных
	db, err := sql.Open("sqlite3", DATABASE)
	if err != nil {
		log.Fatalf("Ошибка подключения к базе данных: %v", err)
		return "0"
	}
	defer db.Close()

	sql := `SELECT hash FROM usrs WHERE usid = $1;`
	// wrkrule, err = db.Exec(sql, usid)
	rows, err := db.Query(sql, usid)

	if err != nil {
		log.Fatalf("Ошибка выполнения запроса: %v", err)
		return "0"
	}
	defer rows.Close()

	count := 0
	for rows.Next() {
		count++
		if count > 1 {
			log.Fatal(errors.New("get_hash, more than one row returned"))
		}
		if err := rows.Scan(&hash); err != nil {
			log.Fatal(err)
		}
	}
	if count == 0 {
		log.Println("get_hash, no hash found")
		usid = 0
	}
	return hash
}

func handlTest(w http.ResponseWriter, r *http.Request, usid int) {
	log.Println("/test", r.Method, r.RemoteAddr)

	file, err := os.ReadFile("./web/test.html")
	if err != nil {
		file = []byte{}
	}
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.WriteHeader(http.StatusOK)
	w.Write(file)
}

func authorized(next func(http.ResponseWriter, *http.Request, int)) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		cookie, err := r.Cookie("token")
		if err != nil {
			log.Println("Ошибка в чтении Cookie", err)
		} else {
			str := cookie.Value
			hash, _ := url.QueryUnescape(str)
			usid := get_user(hash)
			log.Printf("usid from cookies hash %v", usid)
			if usid == 0 {
				http.Redirect(w, r, "/login", http.StatusSeeOther)
				return
			} else {
				next(w, r, usid)
				return
			}
		}

		hash := r.URL.Query().Get("hash")
		log.Println(hash)

		usid := get_user(hash)
		log.Printf("usid from url hash %v", usid)
		if usid == 0 {
			http.Redirect(w, r, "/login", http.StatusSeeOther)
			return
		}

		livingTime := 60 * time.Minute
		expiration := time.Now().Add(livingTime)
		// Перейти на https и установить Secure: true
		// cookie1 := http.Cookie{Name: "token", Value: url.QueryEscape(hash), Expires: expiration, Path: "/test", Secure: false}
		cookie1 := http.Cookie{Name: "token", Value: url.QueryEscape(hash), Expires: expiration}

		http.SetCookie(w, &cookie1)
		next(w, r, usid)

	}
}

func Server() {
	DATABASE, exists := os.LookupEnv("DATABASE")
	if !exists {
		log.Println("Нет DATABASE")
	}

	// Настройка соединения с базой данных
	db, err := sql.Open("sqlite3", DATABASE)
	if err != nil {
		log.Fatalf("Ошибка подключения к базе данных: %v", err)
	}
	defer db.Close()

	// Обработчик для пути /chlst
	http.HandleFunc("/chlst", func(w http.ResponseWriter, r *http.Request) {
		// Выполнение SQL-запроса
		sql := `SELECT c.chid, c.chnm, coalesce(MAX(m.msid), 0) AS MaxX FROM chls c
                    FULL OUTER JOIN mess m  
                    ON c.chid = m.chid
                    WHERE c.chnm <> 'replase_to_invite_url'
                AND c.chid in (
                SELECT DISTINCT usch.chid
                FROM usch usch, usrs usrs
                WHERE 
                    usch.usid = usrs.usid
                    AND usrs.active <> 0
                    AND usrs.istowrk <> 0)
                GROUP BY c.chid;`
		// log.Println(sql)
		rows, err := db.Query(sql)
		if err != nil {
			http.Error(w, fmt.Sprintf("Ошибка выполнения запроса: %v", err), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		// Сканирование результата
		var channels []Channel
		for rows.Next() {
			var ch Channel
			if err := rows.Scan(&ch.ChID, &ch.ChNm, &ch.MsId); err != nil {
				http.Error(w, fmt.Sprintf("Ошибка сканирования данных: %v", err), http.StatusInternalServerError)
				return
			}
			channels = append(channels, ch)
		}

		// Проверка ошибок после итерации
		if err := rows.Err(); err != nil {
			http.Error(w, fmt.Sprintf("Ошибка обработки строк: %v", err), http.StatusInternalServerError)
			return
		}

		// Формирование JSON
		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(channels); err != nil {
			http.Error(w, fmt.Sprintf("Ошибка кодирования JSON: %v", err), http.StatusInternalServerError)
		}
	})

	http.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		w.Header().Set("charset", "utf8")
		w.WriteHeader(http.StatusOK)
		log.Println("Войдите по ссылке Телеграм-бота...")
		rustring := "Войдите по ссылке Телеграм-бота 'Настроить фильтры' https://t.me/Recom777bot"
		// smile := '😀'
		fmt.Fprintf(w, rustring)
		// fmt.Fprintf(w, "%q", smile)
	})

	http.HandleFunc("/svmess", handleSVMess)
	http.HandleFunc("/stfltr", authorized(handleGSFilter))
	http.HandleFunc("/filter", authorized(handleFilter))
	http.HandleFunc("/test", authorized(handlTest))

	fs := http.FileServer(http.Dir("./web/assets"))
	// Путь для файлов js-скриптов и стилей
	http.Handle("/assets/", http.StripPrefix("/assets", fs))

	fslogo := http.FileServer(http.Dir("./web"))
	// Путь для файлов js-скриптов и стилей
	http.Handle("/", http.StripPrefix("/", fslogo))

	// Запуск сервера
	PORT, exists := os.LookupEnv("PORT")
	if !exists {
		log.Println("Не установлен PORT сервера")
	}
	log.Printf("Сервер запущен на порту :%s", PORT)
	if err := http.ListenAndServe(":"+PORT, nil); err != nil {
		log.Fatalf("Ошибка запуска сервера: %v", err)
	}
}
