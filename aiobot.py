import asyncio, sqlite3, re
from datetime import datetime
from datetime import timedelta
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from aiogram.types.input_file import FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from pprint import pprint
from initdb import get_all_channels, get_user_channels, add_all, chedb, get_diff_all_user, get_users, del_all_ch, get_status
from initdb import get_mess_to_send, get_users_to_send, get_text_mess_db, save_sent_mess, get_sndrule, get_ch_name_title
from config import logger, BOT_TOKEN, DATABASE
from telegram.helpers import escape_markdown
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

# start_router = Router()

# bot = Bot(token=BOT_TOKEN)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML', link_preview_is_disabled=True))
dp = Dispatcher()
# Функция экранирования служебных символов MarkdownV2
def esc_Md2(text):
    text = escape_markdown(text)
    # pattern = r"([_*\[\]()~|`.=-!])"
    # pattern = r"([_*\[()~|`.=-!])"
    # text = re.sub(pattern, r"\\\1", text)
    # text = text.replace("_", "\\_")
    # text = text.replace("*", "\\*")
    # text = text.replace("[", "\\[")
    # text = text.replace("`", "\\`")
    text = text.replace("!", "\\!")
    text = text.replace(".", "\\.")
    text = text.replace("-", "\\-")
    return text

# Создает клавиатуру из словаря btns = {"delall":"Удалить все каналы", "read":"Читать сообщения"}
# Не более двух кнопок в ряд
btns_add = {"addall":"Добавить все каналы", "stop":"Остановить рассылку"}
btns_del = {"delall":"Удалить все каналы", "stop":"Остановить рассылку"}
def get_kb(btns):
        km, kb = [], []
        for clbd, text in btns.items():
                kb.append(InlineKeyboardButton(text = text, callback_data=clbd))
                if len(kb) == 2:
                        km.append(kb)
                        kb = []
        if len(kb) > 0:
                km.append(kb)
        keyboard =  InlineKeyboardMarkup(inline_keyboard = km)
        return keyboard

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    usrs = get_users()
    usid = [eu[0] for eu in usrs]
    if message.from_user.id not in usid:
        active, istowrk = True, True
        user_id = message.from_user.id
        name = message.from_user.full_name
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO usrs (usid, username, first_name, last_name, full_name, language_code, isred, lastlog) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, name, message.from_user.language_code, True, datetime.now().isoformat()))
        conn.commit()
        logger.info(f"Добавлен пользователь {name} {user_id}")
    else:
        active, istowrk = get_status(message.from_user.id)
        if istowrk == False:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            sql = f"UPDATE usrs SET istowrk=1 WHERE usid={message.from_user.id}"
            cursor.execute(sql)
            conn.commit()
            logger.info(f"Пользователь {message.from_user.full_name} {message.from_user.id} возобновил рассылку рассылку")
    name = message.from_user.full_name
    if active:
        mess = f"Привет {name}!\n"
        uchls = get_user_channels(message.from_user.id)
        dchls = get_diff_all_user(message.from_user.id)
        uchhttp = ', '.join([f"<a href='https://t.me/{ch[1]}'>{ch[2]}</a>" for ch in uchls]) if uchls else 'нет'
        mess = (f"{mess}Просматриваемые каналы: {uchhttp}\n\n"
        f"Канал можно добавить, отправив в бот сообщение из нужного канала.\n"
        f"Это сообщение также будет использовано в алгоритмах фильтрации.")
        if len(dchls) >= 1:
            dchhttp = ', '.join([f"<a href='https://t.me/{ch[1]}'>{ch[2]}</a>" for ch in dchls])
            mess += f"  \nДобавить все каналы из списка: {dchhttp}"
            await message.answer(mess,
                reply_markup=get_kb(btns_add)
                )
        else:
            await message.answer(mess,
                reply_markup=get_kb(btns_del)
                )
    else:
        mess = f"Ваша учетная запись заблокирована. Обратитесь к администратору."
        await message.answer(mess)
        
@dp.callback_query(F.data.in_(['channels','addall','delall','stop']) )
async def button_press(call: types.CallbackQuery):
    if call.data == 'addall':
        add_all(call.from_user.id)
        uchls = get_user_channels(call.from_user.id)
        dchls = get_diff_all_user(call.from_user.id)
        # uchhttp = ', '.join([f"<a href='https://t.me/{ch[1]}'>{ch[2]}</a>" for ch in uchls]) if uchls else 'нет'
        uchhttp = ', '.join([f"<a href='https://t.me/{ch[1]}'>{ch[2]}</a>" for ch in uchls]) if uchls else 'нет'
        mess = (f"Просматриваемые каналы: {uchhttp}\n\n"
        f"Канал можно добавить, отправив в бот сообщение из нужного канала.\n"
        f"Это сообщение также будет использовано в алгоритмах фильтрации.")
        await call.message.edit_text(mess,
            reply_markup=get_kb(btns_del)
        )
    if call.data == 'delall':
        del_all_ch(call.from_user.id)
        dchls = get_diff_all_user(call.from_user.id)
        mess = (f"Просматриваемые каналы: нет\n\n"
        f"Канал можно добавить, отправив в бот сообщение из нужного канала.\n"
        f"Это сообщение также будет использовано в алгоритмах фильтрации."
        )
        if len(dchls) >= 1:
            dchhttp = ', '.join([f"<a href='https://t.me/{ch[1]}'>{ch[2]}</a>" for ch in dchls])
            mess += f"\nДобавить все каналы из списка: {dchhttp}"
            await call.message.edit_text(mess,
                reply_markup=get_kb(btns_add)
                )
        else:
            await call.message.edit_text(mess,
                reply_markup=get_kb(btns_del)
                )
    if call.data == 'stop':     
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        sql = f"UPDATE usrs SET istowrk=0 WHERE usid={call.from_user.id}"
        cursor.execute(sql)
        conn.commit()
        logger.info(f"Пользователь {call.from_user.full_name} {call.from_user.id} приостановил рассылку")
        mess = f"Отправка сообщений остановлена. Введите /start чтобы возобновить рассылку."
        await call.message.edit_text(mess)  
        
@dp.message()
async def hndltext(message: types.Message):
    # try:
        # Текст сообщения боту или комментария (! - отделить) к пересылаемому сообщению
        msgtext = message.text
        shrttext = msgtext[:50] if msgtext else None
        user_id = message.from_user.id
        sign = 'COMMENT'
        if message.forward_origin:
            # Надо разделить текст комментария. Текст пересылаемого сообщения хранится в таблице mess
            sign = 'FORWARD'
            frwtext = message.caption or message.text
            shrttext = frwtext[:50] if frwtext else None
            if message.forward_origin.chat:
                if message.forward_origin.chat.id:
                    idc = message.forward_origin.chat.id
                    achls = get_all_channels()
                    alchid = [ch[1] for ch in achls]
                    uchls = get_user_channels(user_id)
                    chnm = [ch[1] for ch in uchls]
                    title = message.forward_origin.chat.title
                    msid = message.forward_origin.message_id
                    dtmes = message.forward_origin.date
                    if message.forward_origin.chat.username:
                        name = message.forward_origin.chat.username
                        churl = f'https://t.me/{name}'
                        url = f"https://t.me/{name}/{msid}"
                    else:
                        name = 'replase_to_invite_url'
                        churl = f'https://t.me/{name}'
                        url = f"https://t.me/{name}/{msid}"
                    conn = sqlite3.connect(DATABASE)
                    cursor = conn.cursor()
                    cursor.execute("REPLACE INTO uspr (usid, chid, msid, text, sign, dtadd) VALUES (?, ?, ?, ?, ?, ?)", (user_id, idc, msid, msgtext, sign, datetime.now().isoformat()))
                    cursor.execute("REPLACE INTO mess (chid, msid, text, dtms, dtcl) VALUES (?, ?, ?, ?, ?)", (idc, msid, frwtext, datetime.isoformat(dtmes), datetime.now().isoformat()))
                    if idc not in alchid: 
                        # cursor.execute("REPLACE INTO chls (chid, chnm, title) VALUES (?, ?, ?)", (idm, name, title))
                        sql = f"REPLACE INTO chls (chid, chnm, title, url) VALUES ({idc}, '{name}', '{title}', '{churl}')"
                        cursor.execute(sql)
                        sql = f"REPLACE INTO usch (usid, chid) VALUES ({user_id}, {idc})"
                        cursor.execute(sql)
                        logger.info(f"Канал {name} {idc} добавлен в список каналов {user_id}.")
                        if name == 'replase_to_invite_url':
                            mess = (f"Канал {title} добавлен в список каналов, но для получения "
                                    f"доступа к сообщениям нужны действия администратора.\n"
                                    f"Сообщение '{shrttext}...' сохранено как образец для анализа")
                        else:
                            mess = (f"Канал <a href='{churl}'>{title}</a> добавлен в список каналов.\n"
                                    f"Сообщение '{shrttext}...' сохранено как образец для анализа")
                    elif idc not in chnm:
                        sql = f"REPLACE INTO usch (usid, chid) VALUES ({user_id}, {idc})"
                        cursor.execute(sql)
                        logger.info(f"Канал {name} добавлен в список каналов {user_id}.")
                        if name == 'replase_to_invite_url':
                            mess = (f"Канал {title} добавлен в список каналов, но для получения "
                                    f"доступа к сообщениям нужны действия администратора.\n"
                                    f"Сообщение '{shrttext}...' сохранено как образец для анализа")
                        else:
                            mess = (f"Канал <a href='{churl}'>{title}</a> добавлен в список каналов.\n"
                                f"Сообщение '{shrttext}...' сохранено как образец для анализа")
                    else:
                        if name == 'replase_to_invite_url':
                            mess = (f"Канал {title} уже есть в списке каналов, но для получения "
                                    f"доступа к сообщениям нужны действия администратора.\n"
                                    f"Сообщение '{text[:50]}...' сохранено как образец для анализа")
                        else:
                            mess = (f"Канал <a href='{churl}'>{title}</a> уже есть в списке каналов.\n"
                                f"Сообщение '{shrttext}...' сохранено как образец для анализа")
                    conn.commit()
                    conn.close()
                else:
                    logger.error(f"Ошибка добавления канала. Не найден ID канала. {message}")
                    mess = ("Ошибка добавления канала. Попробуйте еще раз.")
        else:
            # Если это был ответ на какое-то сообщение - отловить это (пока не сделано)
            logger.info(f"Обработка сообщения '{shrttext}...'")
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("REPLACE INTO uspr (usid, text, sign, dtadd) VALUES (?, ?, ?, ?)", (user_id, text, sign, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            if text is not None:
                mess = (f"Сообщение '{shrttext}...' сохранено как образец для анализа")
        await message.answer(mess)
    # except Exception as err:
    #     logger.error(f"{err}\n\n{message}")

def detect_formatting(text):
    markdown_special_chars = r"[_*[\]()~`>#+\-=|{}.!]"
    if re.search(markdown_special_chars, text):
        return 'MarkdownV2'
    return 'HTML'

def escape_dot(text):
    pattern = r"([.!-()-])"
    return re.sub(pattern, r"\\\1", text)

def date_to_local(iso8601_string, timezone_difference_hours = 3):
    # Парсим ISO 8601 строку в datetime объект
    dt = datetime.fromisoformat(iso8601_string)
    # Учитываем разницу в часовых поясах
    adjusted_dt = dt + timedelta(hours=timezone_difference_hours)
    # Преобразуем в нужный формат
    return adjusted_dt.strftime("%Y-%m-%d %H:%M:%S")

kbmess = get_kb({"topic+":"+Тема","topic-":"-Тема","often+":"Чаще этот канал", "often-":"Реже этот канал"})

async def send_mess():
    logger.info(f"Очередная итерация отправки")
    usrs = get_users_to_send()
    logger.info(f"Пользователи: {usrs}")
    for eu in usrs:
        rule = get_sndrule(eu[0])
        mess = get_mess_to_send(eu[0])
        logger.info(f"Сообщения: {mess}")
        for em in mess:
            text, dtms = get_text_mess_db(em[0], em[1])
            ldtms = date_to_local(dtms)
            ch_nm_tl = get_ch_name_title(em[0])
            formatting = detect_formatting(text)
            if formatting == 'MarkdownV2':
                    mess_ts = (f"[{esc_Md2(ch_nm_tl[1])}/{em[1]}]({ch_nm_tl[2]}/{em[1]}) {esc_Md2(ldtms)}   \n  \n{escape_dot(text)}")
            else:
                    mess_ts = (f"<a href='{ch_nm_tl[2]}/{em[1]}'>{ch_nm_tl[1]}/{em[1]}</a> {ldtms} \n\n{text}")  
            # print(mess_ts)
            await bot.send_message(chat_id=eu[0], 
                                   text=mess_ts, 
                                   parse_mode=formatting,
                                   reply_markup=kbmess
                                   )
            save_sent_mess(eu[0], em)

@dp.callback_query(F.data.in_(['topic+','topic-','often+','often-']) )
async def button_press(call: types.CallbackQuery):
        if call.data in ['topic+','topic-','often+','often-']:
            mess = (f"Эта функция пока в разработке")
            await call.message.answer(mess)
        

async def main():
    scheduler.add_job(send_mess, 'interval', seconds=10)
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    print("Start bot")

if __name__ == "__main__":
    asyncio.run(main())