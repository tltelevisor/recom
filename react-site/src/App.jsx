import React, { useEffect, useState, useCallback, useRef } from 'react';
import WordList from './WordList';
import './index.css'

// const FlowApp1 = () => {
export default function App() {


  const baseUrl = `${window.location.protocol}//${window.location.host}`;
  const stfltr = `${baseUrl}/stfltr`

  // const [isapi, setIsapi] = useState(null);
  const [data, setData] = useState([]);

  const getFilter = useCallback(async () => {
    const response = await fetch(stfltr)
    const data = await response.json()
    setData(data)
    setName(data["name"])
    if (data["filter"] != "null") {
      setisAdv(data["filter"]["isadv"])
      setisWh(data["filter"]["iswh"])
      setWhList(data["filter"]["whlist"])
      setisBl(data["filter"]["isbl"])
      setBlList(data["filter"]["bllist"])
      setPhrGPT(data["filter"]["PhrGPT"])
    }
    // setIsapi(1)
  }, [])

  useEffect(() => {
    getFilter()
  }, [getFilter])

  const [name, setName] = useState('Авторизуйтесь через Телеграм');
  const [isAdv, setisAdv] = useState(true);
  const [isWh, setisWh] = useState(false);
  const [Whlist, setWhList] = useState([]);
  const [isBl, setisBl] = useState(false);
  const [Bllist, setBlList] = useState([]);
  const [PhrGPT, setPhrGPT] = useState('');

  const [inputWidth, setInputWidth] = useState(200); // Начальная ширина
  const [inputHeight, setInputHeight] = useState(15); // Начальная высота (высота одной строки)
  const spanRef = useRef(10);

  const [fontSize, setFontSize] = useState('16px');
  const textareaRef = useRef('16px');


  async function setFilter() {
    const filter = { "isadv": isAdv, "iswh": isWh, "whlist": Whlist, "isbl": isBl, "bllist": Bllist, "PhrGPT": PhrGPT }
    try {
      const response = await fetch(stfltr, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filter }),
      });

      if (response.ok) {
        const data = await response.json();
        // setStatus("установлено");
      } else {
        console.log("Ошибка", response)
        // setStatus("Ошибка");
      }
    } catch (error) {
      console.error("Ошибка запроса:", error);
      // setStatus("Ошибка");
    }
  }

  function onChangePhrGPT(e) {
    setPhrGPT(e.target.value)
  }

  // if (isapi) {
  //   return <div>Загрузка...</div>;
  // }
  // else {

    // Обновляем ширину input в зависимости от содержимого
    useEffect(() => {
      if (spanRef.current) {
        const spanElement = spanRef.current;
        const computedStyles = window.getComputedStyle(spanElement);

        // Рассчитываем ширину с учетом ограничений
        const spanWidth = Math.min(spanElement.scrollWidth, window.innerWidth - 20); // 20 — отступы
        const lineHeight = parseFloat(computedStyles.lineHeight || "24"); // Высота строки
        // const newHeight = Math.ceil(spanElement.scrollWidth / (window.innerWidth - 20)) * lineHeight;
        const newHeight = spanRef.current.offsetHeight

        setInputWidth(Math.max(spanWidth, 200)); // Добавляем небольшой отступ
        setInputHeight(Math.max(newHeight, 15));
      }
    }, [PhrGPT]);


    useEffect(() => {
      if (textareaRef.current) {
        const computedStyle = getComputedStyle(textareaRef.current);
        setFontSize(computedStyle.fontSize);
      }
    }, [setFontSize]);

    return (

      <div style={{ padding: '10px' }}>
        <h3>{name}!</h3>
        <h4>Выберите фильтры и их условия</h4>
        <label >
          <input
            type="checkbox"
            value="1"
            checked={isAdv}
            style={{ marginRight: '10px' }}
            onChange={(e) => setisAdv(e.target.checked)}
          />
          Не показывать рекламу
        </label>
        <p></p>
        <label id={"WhLst"}>
          <input
            type="checkbox"
            value="1"
            checked={isWh}
            style={{ marginRight: '10px' }}
            onChange={(e) => setisWh(e.target.checked)}
          />
          Белый список (сообщения только со словами или фразами)
        </label>
        <WordList words={Whlist} setWords={setWhList}></WordList>
        <p></p>
        <label id={"BlLst"}>
          <input
            type="checkbox"
            value="1"
            checked={isBl}
            style={{ marginRight: '10px' }}
            onChange={(e) => setisBl(e.target.checked)}
          />
          Черный список (сообщения, за исключения тех, которые содержат слова или фразы)
        </label>
        <WordList words={Bllist} setWords={setBlList}></WordList>
        <p></p>
        <label htmlFor="textGPT">
          Фраза для ChatGPT для фильтрации сообщений (в ответ ChatGPT или пропустит или не пропустит сообщение в ленту). Фраза построена по шаблону: "Это сообщение "--анализируемое сообщение--" --введенная фраза--. Ответь "да" или "нет"
        </label>
        <p></p>
        <textarea
          // type='text'
          ref={textareaRef}
          value={PhrGPT}
          onChange={onChangePhrGPT}
          className="word"
          placeholder="Фраза для ChatGPT" //"Фраза для ChatGPT"
          style={{
            // ...sharedStyles,
            // marginRight: '10px', padding: '5px', border: '1px solid #ccc', borderRadius: '4px',
            width: `${inputWidth}px`,
            height: `${inputHeight}px`,
            maxWidth: "100%", // Ограничиваем ширину textarea
            overflow: "hidden", // Скрываем скролл
            resize: "none", // Отключаем ручное изменение размеров
            // boxSizing: "border-box",
            transition: "width 0.2s ease, height 0.2s ease",
          }}
        />


        <p></p>
        <button onClick={setFilter}>Применить все изменения</button>
        <p></p>
        {/* Скрытый span для вычисления ширины текста */}
        <div style={{ display: "flex", justifyContent: "flex-start", padding: "6px" }}>
          <span
            ref={spanRef}
            // className="word"
            style={{
              visibility: "hidden",
              whiteSpace: "pre-wrap", // Учитываем перенос строк
              wordBreak: "break-word", // Разбиваем длинные слова
              display: "inline-block",
              // fontSize: "13.3333px",
              fontSize: `${fontSize}`,
              maxWidth: `${window.innerWidth}px`, // Ограничиваем ширину окна
            }}
          >
            {PhrGPT || " "}  {/*Если value пустое, отображаем пробел */}
            {/* {PhrGPT} */}
          </span>
        </div>
      </div>
    );
  };

// }