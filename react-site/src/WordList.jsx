import React, { useState } from 'react';
import './index.css'

// const WordList = () => {
export function WordList({ words = [], setWords = [] }) {

  // const sharedStyles = {
  //   fontFamily: "Arial, sans-serif",
  //   fontSize: "16px",
  //   fontWeight: "400",
  //   letterSpacing: "0.5px",
  //   lineHeight: "1px",
  //   padding: "4px",
  //   boxSizing: "border-box",
  // };

  // Состояние для нового слова
  const [newWord, setNewWord] = useState('');

  // Функция для добавления нового слова
  const addWord = () => {
    if (newWord.trim()) {
      setWords([...words, newWord.trim()]); // Добавляем слово в список
      setNewWord(''); // Очищаем поле ввода

    }
  };

  // Функция для удаления слова по индексу
  const removeWord = (index) => {
    setWords(words.filter((_, i) => i !== index));

  };
  return (
    <div >
      <ul>
        {words.map((word, index) => (
          <li key={index} style={{ marginBottom: '10px' }}>
            {word}{' '}
            <button
              onClick={() => removeWord(index)}
              className="sm_button"
              style={{ color: 'red' }}
            >
              ✕
            </button>
          </li>
        ))}
      </ul>

      <div style={{display: 'flex', alignItems: 'center'}}>
          <textarea
            // type="text"
            value={newWord}
            className="word"
            onChange={(e) => setNewWord(e.target.value)}
            placeholder="Слово или фраза"
          />
          <button
            onClick={addWord}
            className="sm_button"
            style={{ color: 'green' }}
          >
            +
          </button>
      </div>
    </div>
  );
};

export default WordList;
