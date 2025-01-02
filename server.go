package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

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

// func openDB() (*sql.DB, error) {
// 	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
// 		dbHost, dbPort, dbUser, dbPassword, dbName)
// 	return sql.Open("postgres", psqlInfo)
// }

// func insertMessage(db *sql.DB, msg Message) error {
// 	query := "INSERT INTO mess (id, content) VALUES ($1, $2)"
// 	_, err := db.Exec(query, msg.ID, msg.Content)
// 	return err
// }

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

	http.HandleFunc("/svmess", handleSVMess)

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
