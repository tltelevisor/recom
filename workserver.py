from config import logger, DATABASE, HOURS_TO_LIVE
#from telethon import TelegramClient
from initdb import get_users_to_work, get_mess_to_work, get_wrkrule, get_text_mess_db, get_config_param
from oai import PhrGPT
from datetime import datetime, timedelta
from timesleep import time_to_sleep_f
from time import sleep
import sqlite3, ast
import nltk

# nltk.download('popular')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
stop_words = set(stopwords.words('russian'))
stemmer = SnowballStemmer("russian")



def isadv(mess_tok):
    adv_lst_text = get_config_param('adv_lst')
    adv_lst = ast.literal_eval(adv_lst_text)
    for ew in adv_lst:
        tokens = word_tokenize(ew)
        logger.info(tokens)
        stemmed_words = stemmer.stem(tokens[0])
        if stemmed_words in mess_tok:
            return 1
    return 0

def whlist(wl,mess_tok):
    for ew in wl:
        tokens = word_tokenize(ew)
        stemmed_words = stemmer.stem(tokens[0])
        if stemmed_words in mess_tok:
            return 1
    return 0

def bllist(wl,mess_tok):
    for ew in wl:
        tokens = word_tokenize(ew)
        stemmed_words = stemmer.stem(tokens[0])
        if stemmed_words in mess_tok:
            return 1
    return 0

def delete_old_mess(nwdt):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    sql = f'''SELECT count(*) FROM mess WHERE dtms < "{nwdt}";'''
    cursor.execute(sql)
    rows = cursor.fetchone()[0]
    sql = f'''DELETE FROM mesus WHERE EXISTS (
                    SELECT 1
                    FROM mess
                    WHERE mess.chid = mesus.chid 
                    AND mess.msid = mesus.msid
                    AND mess.dtms < "{nwdt}");'''
    cursor.execute(sql)
    sql = f'''DELETE FROM mess WHERE dtms < "{nwdt}"'''
    cursor.execute(sql)
    conn.commit()
    conn.close()
    logger.info(f"Удалено {rows} обработанных сообщений")

def work_mess(wrkrule, text):
    wrkdic = ast.literal_eval(wrkrule.replace("true", "True").replace("false", "False"))
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in stop_words]
    stemmed_words = [stemmer.stem(word) for word in filtered_tokens]
    if wrkdic["filter"]["isadv"]:
        if isadv(stemmed_words):
            logger.info(f"сообщение отброшено по признаку рекаламы")
            return 0
    if wrkdic["filter"]["iswh"]:
        if whlist(wrkdic["filter"]["whlist"], stemmed_words):
            logger.info(f"сообщение к отправке по признаку белого списка")
            return 1
        else:
            logger.info(f"сообщение отброшено, так как не прошло по признаку белого списка")
            return 0
    if wrkdic["filter"]["isbl"]:
        if bllist(wrkdic["filter"]["bllist"], stemmed_words):
            logger.info(f"сообщение отброшено по признаку черного списка")
            return 0
    if wrkdic["filter"]["PhrGPT"]:
        rs_gpt = PhrGPT(wrkdic["filter"]["PhrGPT"], text)
        if rs_gpt[0]:
            if rs_gpt[1]:
                logger.info(f"сообщение к отправке по решению ChatGPT")
                return 1
            else:
                logger.info(f"сообщение отброшено по решению ChatGPT")
                return 0
        else:
            logger.info(f"ChatGPT не доступен, сообщение к отправке")
            return 1      
    return 0

def work_serv():
    logger.info(f"Start workserver")
    while True:
        dt_to_del = datetime.now() - timedelta(hours=HOURS_TO_LIVE)
        usrs = get_users_to_work()
        if len(usrs) > 0:
            delete_old_mess(dt_to_del)
            # logger.info(f"Старт обработки сообщений для пользователей: {usrs}")
            # Выбрать сообщения для обработки с учетом времени
            for usr in usrs:
                mess = get_mess_to_work(usr[0])
                if len(mess) > 0:
                    wrkrule = get_wrkrule(usr[0])
                    logger.info(f"Обработка {mess} сообщений для пользователя {usrs}, wrkrule: {wrkrule}")
                    for em in mess:
                        text, _ = get_text_mess_db(em[0], em[1])
                        istsnd = work_mess(wrkrule, text)
                        conn = sqlite3.connect(DATABASE)
                        cursor = conn.cursor()
                        sql = f"UPDATE mesus SET iswrk=1, dtwrk='{datetime.now().isoformat()}', istsnd={istsnd} WHERE chid={em[0]} AND msid={em[1]} AND usid={usr[0]};"
                        cursor.execute(sql)
                        conn.commit()
                        conn.close()
                        sleep(1)
        sleep(5)

if __name__ == '__main__':
    work_serv()