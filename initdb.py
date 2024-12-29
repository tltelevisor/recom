from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext #Filters,
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import sqlite3, asyncio
from config import logger, DATABASE, CHANNELS, API_ID, API_HASH, NAME
from telethon import TelegramClient

  
async def get_chnl_id(chnl):
    async with TelegramClient(NAME, API_ID, API_HASH) as client:
        try:
            channel = await client.get_entity(chnl)
        except Exception as e:
            logger.error(f"Ошибка получения канала: {e}")
        return channel.id, channel.title

async def set_chanls():
    chls = get_all_channels()
    chnm_ls = [er[1] for er in chls] if chls else []
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    for chnl in CHANNELS:
        if chnl not in chnm_ls:
            chid, title = await get_chnl_id(chnl)
            churl = f'https://t.me/{chnl}'
            cursor.execute("REPLACE INTO chls (chid, chnm, title, url) VALUES (?, ?, ?, ?)", (chid, chnl, title, churl))
            conn.commit()
    conn.close()

# Создание базы данных для хранения предпочтений пользователей
async def init_db():
    try:
        usrs = '''CREATE TABLE IF NOT EXISTS usrs (
                            usid INTEGER PRIMARY KEY,
                            username TEXT,
                            first_name TEXT,
                            last_name TEXT,
                            full_name TEXT,
                            language_code TEXT,
                            isred BOOLEAN default 0,
                            lastlog datetime,
                            wrkrule TEXT,
                            sndrule TEXT,
                            active BOOLEAN default 1,
                            istowrk BOOLEAN default 1
                        )'''
        #chnl_id INTEGER
        chls = '''CREATE TABLE IF NOT EXISTS chls (
                        chid INTEGER PRIMARY KEY,
                        chnm TEXT,
                        title TEXT,
                        url TEXT
                    )'''                
        usch = '''CREATE TABLE IF NOT EXISTS usch (
                    usid INTEGER, 
                    chid TEXT, 
                    PRIMARY KEY (usid, chid),
                    FOREIGN KEY (usid) REFERENCES usrs(usid),
                    FOREIGN KEY (chid) REFERENCES chls(chid)
                )'''    
        mess = '''CREATE TABLE IF NOT EXISTS mess (
                    chid INTEGER, 
                    msid INTEGER,
                    dtms datetime,
                    dtcl datetime,
                    text TEXT,
                    isuspr BOOLEAN default 0,
                    PRIMARY KEY (chid, msid),
                    FOREIGN KEY (chid) REFERENCES chls(chid)
                )'''
        mesus = '''CREATE TABLE IF NOT EXISTS mesus (
                    chid INTEGER,
                    msid INTEGER,
                    usid INTEGER,
                    iswrk BOOLEAN default 0,
                    dtwrk datetime default 0,
                    istsnd BOOLEAN default 0,
                    issnt BOOLEAN default 0,
                    dtsnt datetime,
                    PRIMARY KEY (chid, msid, usid),
                    FOREIGN KEY (chid) REFERENCES usrs(usid),
                    FOREIGN KEY (msid) REFERENCES mess(msid),
                    FOREIGN KEY (usid) REFERENCES usrs(usid)
                )'''
        uspr = '''CREATE TABLE IF NOT EXISTS uspr (
                    prid INTEGER PRIMARY KEY,
                    usid INTEGER,
                    chid INTEGER,
                    msid INTEGER,
                    text TEXT,
                    sign TEXT,
                    dtadd datetime,
                    FOREIGN KEY (usid) REFERENCES usrs(usid),
                    FOREIGN KEY (chid) REFERENCES chls(chid),
                    FOREIGN KEY (msid) REFERENCES mess(msid)
                );
                    '''
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(usrs)
        cursor.execute(chls)
        cursor.execute(usch)
        cursor.execute(mess)
        cursor.execute(mesus)
        cursor.execute(uspr)
        await set_chanls()
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return f"Ошибка инициализации базы данных: {e}"
    return "База данных инициализирована"

def get_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT usid, username, first_name, last_name, language_code FROM usrs")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_status(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT  active, istowrk FROM usrs WHERE usid = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_user_channels(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT c.chid, c.chnm, c.title FROM chls c JOIN usch u ON c.chid = u.chid AND u.usid = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_diff_all_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT chid, chnm, title FROM chls WHERE chid NOT IN (SELECT chid FROM usch WHERE usid = ?)", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_channels():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT chid, chnm, title FROM chls ORDER BY chnm")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_all(user_id):
    chls = get_all_channels()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    for ech in chls:
        cursor.execute("REPLACE INTO usch (usid, chid) VALUES (?, ?)", (user_id, ech[0]))
    conn.commit()
    conn.close()

def chedb():
    chls = get_all_channels()
    if len(chls) < len(CHANNELS):
        return False
    return True
def ch_to_serv():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    sql = '''SELECT chid, chnm FROM chls 
                WHERE chnm <> 'replase_to_invite_url'
                AND chid in (
                SELECT DISTINCT usch.chid
                FROM usch usch, usrs usrs
                WHERE 
                    usch.usid = usrs.usid
                    AND usrs.active <> 0
                    AND usrs.istowrk <> 0
                )'''
    # cursor.execute("SELECT chid, chnm FROM chls WHERE chid in (SELECT DISTINCT chid from usch) AND chnm <> 'replase_to_invite_url'")
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def mess_ch(chid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT msid FROM mess WHERE chid = ?", (chid,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_ch_name_title(chid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT chnm, title, url FROM chls WHERE chid = ?", (chid,))
    rows = cursor.fetchone()
    conn.commit()
    return rows

def get_mess_to_send(usid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    sql = '''SELECT m.chid, m.msid FROM mesus m 
                WHERE m.chid in (
                SELECT chid from usch WHERE usid = ?)
                AND m.istsnd = 1
                AND m.issnt = 0'''
    cursor.execute(sql, (usid,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_mess_to_work(usid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    sql ='''SELECT m.chid, m.msid FROM mesus m 
                WHERE m.usid = ?
                AND not m.iswrk
                ORDER by m.chid, m.msid '''
    cursor.execute(sql, (usid,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_wrkrule(usid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    rule = cursor.execute(f"SELECT u.wrkrule FROM usrs u WHERE u.usid = {usid}").fetchone()[0]
    conn.commit()
    conn.close()
    return rule

def get_sndrule(usid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    rule = cursor.execute(f"SELECT u.sndrule FROM usrs u WHERE u.usid = {usid}").fetchone()[0]
    conn.commit()
    conn.close()
    return rule

def int_sent_mess(usid):
    rule = get_wrkrule(usid)
    # ism = metafunc(rule, ism)
    ism = 24 #
    return ism

def get_sent_mess(usid):
    ism = int_sent_mess(usid)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    sql =(f"SELECT * FROM mesus m " 
            f"WHERE m.usid = {usid} "
            f"AND (m.issnt or m.istsnd) "
            f"AND dtsnt > datetime('now', '-{ism} hours') "
            f"ORDER by m.chid, m.msid;")
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_users_to_work():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    sql = '''SELECT DISTINCT m.usid FROM mesus m 
            WHERE m.iswrk = 0
            AND m.usid not in (
            SELECT u.usid FROM usrs u
            WHERE u.active = 0 
            AND u.istowrk = 0)
         '''
    # cursor.execute("SELECT DISTINCT m.usid FROM mesus m WHERE m.iswrk = 0")
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_users_to_send():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    sql = '''SELECT DISTINCT m.usid FROM mesus m 
                WHERE m.istsnd = 1
                AND m.usid not in (
                SELECT u.usid FROM usrs u
                WHERE u.active = 0 
                AND u.istowrk = 0)
            '''
    # cursor.execute("SELECT DISTINCT m.usid FROM mesus m WHERE m.istsnd = 1")
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def work_mess(usr, mess):
    rule = get_wrkrule(usr)
    snt_mess = get_sent_mess(usr)
    # mess_tsnd = f(rule, mess, snt_mess)
    mess_tsnd = mess
    for em in mess_tsnd:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        sql = f"UPDATE mesus SET iswrk=1, dtwrk='{datetime.now().isoformat()}', istsnd=1 WHERE chid={em[0]} AND msid={em[1]} AND usid={usr};"
        cursor.execute(sql)
        conn.commit()
        conn.close()

def save_sent_mess(usr, em):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    sql = f"UPDATE mesus SET issnt=1, dtsnt='{datetime.now().isoformat()}' WHERE chid={em[0]} AND msid={em[1]} AND usid={usr};"
    cursor.execute(sql)
    conn.commit()
    conn.close()

 
def get_text_mess_db(chid, msid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT text, dtms FROM mess WHERE chid = ? AND msid = ?", (chid, msid))
    text, dtms = cursor.fetchone()
    conn.commit()
    conn.close()
    return text, dtms

def del_all_ch(usid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usch WHERE usid = ?", (usid,))
    conn.commit()
    conn.close()
    

if __name__ == '__main__':
    res = asyncio.run(init_db())
    logger.info(res)
    print(res)