from config import logger, API_ID, API_HASH, NAME, DATABASE
from telethon import TelegramClient
from initdb import get_users_to_work, get_mess_to_work, work_mess
from datetime import datetime
from timesleep import time_to_sleep_f
from time import sleep
import sqlite3

def textmess():
    pass
    return 
"""
    # Вариант запроса сообщений из Телеграм
    with TelegramClient(NAME, API_ID, API_HASH) as client:
        lst_mess = []
        try:
            chnm, ml = mess[0][0], []
            for em in mess:
                if em[0] == chnm:
                    ml.append(em[1])
                else:
                    messages = client.iter_messages(em[0], ids = ml)
                    for emt in messages:
                        lst_mess.append(emt)
                    logger.info(f"Получено {len(ml)} сообщений для обработки из канала {chnm}")
                    chnm, ml = em[0], []
                    sleep(time_to_sleep_f(20)[2])
            messages = client.iter_messages(em[0], ids = ml)
            for emt in messages:
                lst_mess.append(emt)
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {e} в канале {chnm}")
"""


def work_serv():
    while True:
        usrs = get_users_to_work()
        if len(usrs) > 0:
            logger.info(f"Старт обработки сообщений для пользователей: {usrs}")
        # Выбрать сообщения для обработки с учетом времени
        for usr in usrs:
            mess = get_mess_to_work(usr[0])
            logger.info(f"Сообщений для обработки {len(mess)}")
            work_mess(usr[0], mess)
        sleep(5)

if __name__ == '__main__':
    work_serv()