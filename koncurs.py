from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
import sqlite3
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
API_key = os.getenv("API_KOD")

bot = telebot.TeleBot(API_key)

def log_gifts(gift_name):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO gifts (gift_name)
        VALUES (?)
        """, (gift_name,))

        conn.commit()

    except sqlite3.Error as e:
        print("Error logging user:", e)
    finally:
        conn.close()


def get_top_referrers():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, referrals FROM kon_users ORDER BY referrals DESC LIMIT 10")
    return cursor.fetchall()

def find_name(user_id):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    people = cursor.fetchall()
    for p in people:
        if user_id == p[1]:
            if p[2] != None:
                return p[2]
            else:
                return p[3]


def top_referrers_handler(message: types.Message):
    top_referrers = get_top_referrers()
    if not top_referrers:
        bot.reply_to(message, "No referrals yet!")
        return

    # Format the leaderboard message
    leaderboard = "🏆 Top 10 Referrers:\n\n"
    for rank, (user_id, count) in enumerate(top_referrers, start=1):
        us_name = find_name(user_id)
        leaderboard += f"{rank}.{us_name}: {count}\n"


    bot.send_message(message.chat.id, leaderboard)



def prize(message):


    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gifts")
    pr = cursor.fetchall()
    try:
        bot.send_message(message.chat.id, f"{pr[0][1]}\n{pr[1][1]}\n{pr[2][1]}\nXabar ko'rinishi shunga o'xshash bo'lsin.🤨")
    except:
        log_gifts("1- ________________")
        log_gifts("2- ________________")
        log_gifts("3- ________________")
        log_gifts("3.01.2025 (Juma kuni tugaydi)")
        log_gifts("referal yig'ish (Nakrutka urgan odam ban)")
        cursor.execute("SELECT * FROM gifts")
        pr = cursor.fetchall()
        bot.send_message(message.chat.id, f"{pr[0][1]}\n{pr[1][1]}\n{pr[2][1]}\nXabar ko'rinishi shunga o'xshash bo'lsin.🤨")


def taking_prizes(message):

    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    presents: list = message.text.split("\n")
    try:
        cursor.execute("UPDATE gifts SET gift_name = ? WHERE id = ?", (presents[0], 1))
        cursor.execute("UPDATE gifts SET gift_name = ? WHERE id = ?", (presents[1], 2))
        cursor.execute("UPDATE gifts SET gift_name = ? WHERE id = ?", (presents[2], 3))
        conn.commit()
        bot.send_message(message.chat.id, "✅Yangi yutuqlar muvaffaqiyatli o'rnatildi.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⛔️Tizimda xatolik ketdi: {e}")


def rues(message):


    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gifts")
    pr = cursor.fetchall()
    try:
        bot.send_message(message.chat.id, f"{pr[3][1]}\n{pr[4][1]}\nXabar ko'rinishi shunga o'xshash bo'lsin.🤨")
    except:
        bot.send_message(message.chat.id, f"Referal yigish ...\n10.01.2025...\nXabar ko'rinishi shunga o'xshash bo'lsin.🤨")



def taking_rules(message):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    presents: list = message.text.split("\n")
    try:
        cursor.execute("UPDATE gifts SET gift_name = ? WHERE id = ?", (presents[0], 4))
        cursor.execute("UPDATE gifts SET gift_name = ? WHERE id = ?", (presents[1], 5))
        bot.send_message(message.chat.id,"✅Yangi qoidalar muvaffaqiyatli o'rnatildi.")
        conn.commit()
    except Exception as e:
        bot.send_message(message.chat.id, f"⛔️Tizimda xatolik ketdi: {e}")



def kon_start(message, kon_holat):

    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="📊O'rinlar ro'yhati", callback_data="show_list_kon")
    keyboard.add(button1)
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gifts")
    pr = cursor.fetchall()
    rules = pr[4][1]
    kun = pr[3][1]
    cursor.execute("SELECT * FROM kon_users")
    people = cursor.fetchall()
    count = 0
    for p in people:
        if p[1] == message.chat.id:
            count = p[2]
            break
    bot.send_message(message.chat.id,
                     f"🎉Biz Dream Anime jamoasi\n Konkursimizga start berdik !!!\n✏️Qoidalar : {rules[1]}\n🎁So'vrinlar\n🎁{pr[0][1]}\n🎁{pr[1][1]}\n🎁{pr[2][1]}\nHammaga omad\nKonkursimiz {kun[1]}\nQantashish uchun botga o'tib Konkurs knopkasini bosing!!!\n────────────────\n🔥Sizning taklif havolangiz : https://t.me/{bot.get_me().username}?start={message.chat.id}\n-\n🖇Sizning takliflaringiz : {count}\n-\n{kon_holat}",
                     reply_markup=keyboard)

def kon_stop(message):
    kon_holat = "🔴Konkurs tugagan"
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gifts")
    people = cursor.fetchall()
    for p in people:
        cursor.execute("UPDATE kon_users SET referrals = ? WHERE user_id = ?", (0,p[1]))
        conn.commit()
    bot.send_message(message.chat.id, text = "Konkurs to'xtatildi.⛔️")



