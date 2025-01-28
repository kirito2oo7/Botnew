import os
from telebot import types
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot



from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
API_key = os.getenv("API_KOD")
bot_username = os.getenv("BOT_USERNAME")


bot = telebot.TeleBot(API_key)
bmd = "CAACAgIAAxkBAAIBlmdxZi6sK42VCA3-ogaIn30MXGrmAAJnIAACKVtpSNxijIXcPOrMNgQ"

def is_admin(user_id):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins")
    ids_of_admin = cursor.fetchall()
    for x in ids_of_admin:
        if user_id == x[1]:
            return True
    return False


def main_keyboard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_Ai = types.KeyboardButton('🔎Anime izlash')
    item_KN = types.KeyboardButton("🎁Konkurs")
    item_RK = types.KeyboardButton("💵Reklama va Homiylik")
    markup.row(item_Ai)
    markup.row(item_KN, item_RK)
    if is_admin(message.chat.id):
        item_BH = types.KeyboardButton(text="🛂Boshqaruv")
        markup.row(item_BH)
    return markup

def get_file(file_kod):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute('SELECT  file_id, file_name, file_type FROM files WHERE file_kod = ?', (file_kod,))
    file = cursor.fetchall()
    conn.close()
    return file

def check_user_in_channel(message):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM followers")
    ll = cursor.fetchall()

    for i in ll:
        try:
            s:str = i[2]
            url1: str = f"@{s[13:]}"
            member = bot.get_chat_member(chat_id= url1, user_id = message.chat.id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"channel_Error: {e}")
            return False
    return True


def log_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect("bot_users.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        """, (user_id, username, first_name, last_name))
        conn.commit()

    except sqlite3.Error as e:
        print("Error logging user:", e)
    finally:
        conn.close()

def send_link(message, kon_holat):
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="📊O'rinlar ro'yhati", callback_data= "show_list_kon")
    keyboard.add(button1)
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gifts")
    pr = cursor.fetchall()
    rules = pr[4]
    kun = pr[3]
    cursor.execute("SELECT * FROM kon_users")
    people = cursor.fetchall()
    count = 0
    for p in people:
        if p[1] == message.chat.id:
            count = p[2]
            break
    bot.send_message(message.chat.id,
                     f"🎉Biz Dream Anime jamoasi\n Konkursimizga start berdik !!!\n✏️Qoidalar : {rules[1]}\n🎁So'vrinlar\n🎁{pr[0][1]}\n🎁{pr[1][1]}\n🎁{pr[2][1]}\nHammaga omad\nKonkursimiz {kun[1]}\nQantashish uchun botga o'tib Konkurs knopkasini bosing!!!\n────────────────\n🔥Sizning taklif havolangiz : https://t.me/{bot.get_me().username}?start={message.chat.id}\n-\n🖇Sizning takliflaringiz : {count}\n-\n{kon_holat}",
                     reply_markup= keyboard)


def log_referal(user_id,referrals):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO kon_users (user_id, referrals)
        VALUES (?, ?)
        """, (user_id, referrals))
        conn.commit()

    except sqlite3.Error as e:
        print("Error logging user:", e)
    finally:
        conn.close()

def handle_start_button(call):
    bot.answer_callback_query(call.id, "Sending /start command...")
    print(check_user_in_channel(call.message))
    if check_user_in_channel(call.message):
        conn = sqlite3.connect("bot_users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM followers")
        ll = cursor.fetchall()
        for chan in ll:
            s:str = chan[2]
            n: int = chan[4]
            print(s,n)
            cursor.execute("UPDATE followers SET now_follower = ? WHERE channel_url = ?", (n + 1, s))
            conn.commit()
            m:int = chan[3]
            if n >= m:
                cursor.execute("DELETE FROM followers WHERE channel_url = ?", (s,))
                conn.commit()

                bot.send_message(call.message.chat.id, f"✅ {chan[1]} kanal {n} ta obunachi qo'shilgani uchun o'chirildi")


def check_user_in_referrals(user_id):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kon_users")
    people = cursor.fetchall()
    for p in people:
        if user_id in p:
            return False
    return True


def send_welcome(message: types.Message, konkurs_switch, kon_holat):
    args = message.text.split()

    user = message.from_user

    log_user(user.id, user.username, user.first_name, user.last_name)
    file_kod = None


    if check_user_in_channel(message):

        bot.send_message(message.chat.id,"Assalomu alaykum, bu Dream Anime boti. Qanday yordam bera olaman ?", reply_markup=main_keyboard(message))
        try:
            if len(args) > 1 and int(args[1]) < 1e8:
                file_kod = int(args[1])
                bot.send_message(message.chat.id, "Searching....")
                file_n_i = get_file(file_kod)

                k = 0
                for f in file_n_i:
                    if f:
                        saved_file_id, file_name, file_type = f
                        k += 1
                        # Send file using its file_id

                        if file_type == 'photo':
                            bot.send_photo(message.chat.id, saved_file_id, caption=file_name)

                        elif file_type == 'video':
                            bot.send_video(message.chat.id, saved_file_id, caption=f"{k} - qism")

                        else:
                            bot.reply_to(message, "⭕️Unknown file type.")
                    else:
                        bot.reply_to(message, "⭕️File not found.")

        except Exception as e:
            print(e)
        finally:
            print("----")

    else:
        try:
            if len(args) > 1 and int(args[1]) < 1e8:
                file_kod = int(args[1])
            else:
                file_kod = None
        except:
            file_kod = None
        conn = sqlite3.connect("bot_users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM followers")
        l = cursor.fetchall()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📱 Instagram", url="https://www.instagram.com/anime_kirito_2oo7"))
        for c in l:
            print("c =", c[1], c[2])
            keyboard.add(InlineKeyboardButton(text= c[1], url= c[2]))
        if file_kod != "":
            start_button = InlineKeyboardButton("✅Tekshirish", url= f"https://t.me/{bot_username}?start={file_kod}")
        else:
            start_button = InlineKeyboardButton("✅Tekshirish", callback_data="send_start")
        keyboard.add(start_button)

        bot.send_message(message.chat.id, f"Assalomu alaykum \nAgar bizning xizmatlarimizdan foydalanmoqchi bo'lsangiz, Iltimos pastdagi kanallarga obuna bo'ling!",reply_markup=keyboard)
        bot.send_sticker(message.chat.id, sticker = bmd)


    if len(args) > 1 and konkurs_switch:
        ref_id = args[1]
        if ref_id != str(user.id) and check_user_in_referrals(user.id):
            conn = sqlite3.connect("bot_users.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kon_users")
            people = cursor.fetchall()
            for p in people:
                if int(p[1]) != int(ref_id):
                    cursor.execute("UPDATE kon_users SET referrals = ? WHERE user_id = ?", (p[2] + 1, ref_id))
                    conn.commit()
            log_referal(user.id, 0)
        send_link(message, kon_holat)
    else:
        log_referal(user.id, 0)








