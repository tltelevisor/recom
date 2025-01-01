from config import logger, API_ID, API_HASH, NAME, DATABASE, MSG_LIMIT
from telethon import TelegramClient
from initdb import ch_to_serv, mess_ch
from datetime import datetime
from timesleep import time_to_sleep_f
from time import sleep
import sqlite3


# Функцияз получения сообщений из каналов
# Запускается на сервере, где база данных
def getmess():
    while True:
        chls = ch_to_serv()
        logger.info(f"Старт обновления каналов: {chls}")
        with TelegramClient(NAME, API_ID, API_HASH) as client:
            try:
                for ch in chls:
                    logger.info(f"Канал: {ch}")
                    msgs_db_tp = mess_ch(ch[0])
                    msgs_db = [int(msg[0]) for msg in msgs_db_tp]
                    messages = client.iter_messages(ch[1], limit=MSG_LIMIT)
                    # logger.info(f"сообщения: {msgs_db}")
                    nmm = 0
                    for msg in messages:
                        # logger.info(f"Сообщение: {msg.id}")
                        msgid = int(msg.id)
                        if msgid not in msgs_db:
                            nmm += 1
                            conn = sqlite3.connect(DATABASE)
                            cursor = conn.cursor()
                            cursor.execute("REPLACE INTO mess (chid, msid, text, dtms, dtcl) VALUES (?, ?, ?, ?, ?)", (int(ch[0]), msgid, msg.text, datetime.isoformat(msg.date), datetime.now().isoformat()))
                            sql=(f"REPLACE INTO mesus (chid, msid, usid)" 
                                 f" SELECT {ch[0]}, {msgid}, usid from usch u WHERE u.chid = {ch[0]}")
                            # logger.info('sql', sql)
                            cursor.execute(sql)
                            conn.commit()
                            continue
                    logger.info(f"Добавлено {nmm} сообщений из канала {ch}")
                    sleep(time_to_sleep_f(20)[2])
            except Exception as e:
                logger.error(f"Ошибка получения сообщений: {e}, {ch}")
        tts = time_to_sleep_f()[2]
        logger.info(f"Sleep {tts} seconds")
        sleep(tts)

if __name__ == '__main__':
    getmess()