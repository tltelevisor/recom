from gconfig import logger, CHLST_URL,NAME, API_ID, API_HASH, MSG_LIMIT, SVMESS_URL
from telethon import TelegramClient
from datetime import datetime
from timesleep import time_to_sleep_f
from time import sleep
import urllib.request, json
import requests, random

# client = TelegramClient(StringSession(SESSION_STRING), api_id=API_ID, api_hash=API_HASH, device_model="Linux 5.15.0", system_version="Ubuntu 20.04.6 LTS")
# client.session.save()

# Функцияз получения сообщений из каналов
# Запускается на удаленном сервере
def cicle_getmess_remote():
    while True:
        getmess_remote()
        # tts = time_to_sleep_f()[2]
        tts = int(360 * (1 - random.uniform(0, 0.5)))
        logger.info(f"Sleep {tts} seconds")
        sleep(tts)

def getmess_remote():
        response = urllib.request.urlopen(CHLST_URL)#.read()
        encoding = response.info().get_content_charset('utf8')
        chls = json.loads(response.read().decode(encoding))
        # print(data)
        # print(type(data))
        # chls = ch_to_serv()
        logger.info(f"Старт обновления каналов: {chls}")
        with TelegramClient(NAME, API_ID, API_HASH) as client:
            try:
                # print(chls)
                # print(type(chls))
                # print(chls[0])
                for ch in chls:
                    logger.info(f"Канал: {ch}")
                    messages = client.iter_messages(ch['chnm'], min_id = int(ch['msid']),limit=MSG_LIMIT)
                    # logger.info(f"сообщения: {msgs_db}")
                    nmm = 0
                    for msg in messages:
                        logger.info(f"Сообщение: {ch['chnm']}, {msg.id}")
                        dic_msg = {'chid':ch['chid'], 'msid':msg.id, 'text':msg.text, 'dtms':datetime.isoformat(msg.date), 'dtcl':datetime.now().isoformat()} 
                        resp = requests.post(SVMESS_URL, json = dic_msg)
                        if resp.status_code != 200:
                            logger.error(f"Ошибка добавления сообщения на сервере: {resp.text}")
                        else:
                            nmm += 1
                    logger.info(f"Добавлено {nmm} сообщений из канала {ch}")
                    ttsl = int(20 * (1 - random.uniform(0, 0.5))) #time_to_sleep_f(20)[2]
                    logger.info(f"Sleep {ttsl} seconds")
                    sleep(ttsl)
            except Exception as e:
                logger.error(f"Ошибка получения сообщений: {e}, {ch}")

if __name__ == '__main__':
    cicle_getmess_remote()