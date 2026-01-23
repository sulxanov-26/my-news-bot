import requests, telebot, os, time
from telebot import types
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup

# 1. SERVER SOZLAMASI
app = Flask('')
@app.route('/')
def home(): return "Bot Live! ✅"

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# TOKEN VA ADMIN ID (Eslatma uchun)
TOKEN = "8468486478:AAGKuA5lJ-VFXOKld5KKNoz4bRFmjeueYOM"
ADMIN_ID = "6102146115" # O'zingizning ID raqamingizni yozing
bot = telebot.TeleBot(TOKEN)

# 2. KESH VA ESLATMA UCHUN O'ZGARUVCHILAR
weather_cache = {}
currency_state = {"last_rate": None}

# OB-HAVO FUNKSIYASI (ANIQ GRADUSDA)
def get_weather(city_en):
    try:
        url = f"https://wttr.in/{city_en}?format=%c+%t&m"
        r = requests.get(url, timeout=10)
        uz_names = {"Tashkent":"Toshkent", "Samarkand":"Samarqand", "Andijan":"Andijon", "Fergana":"Farg'ona", "Namangan":"Namangan", "Bukhara":"Buxoro", "Navoi":"Navoiy", "Karshi":"Qarshi", "Termez":"Termiz", "Nukus":"Nukus", "Guliston":"Guliston", "Jizzakh":"Jizzax", "Urgench":"Urganch"}
        temp = r.text.strip().replace('+', '')
        return f"🌤 {uz_names.get(city_en, city_en)}: {temp}"
    except: return "⚠️ Ob-havo ma'lumotida xato."

# VALYUTA O'ZGARISHINI TEKSHIRISH (ESLATMA)
def check_currency_update():
    while True:
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            current_usd = r[0]['Rate']
            if currency_state["last_rate"] and currency_state["last_rate"] != current_usd:
                msg = f"🔔 **DIQQAT! Valyuta kursi o'zgardi!**\n\n💵 1 USD = {current_usd} so'm"
                bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")
            currency_state["last_rate"] = current_usd
        except: pass
        time.sleep(3600) # Har 1 soatda tekshiradi

# 3. KINOLAR BAZASI (120 TA FILM)
def get_movies(genre_key):
    movies = {
        "k_1": [("Jon Uik 1", "https://t.me/c/123/1"), ("Jon Uik 2", "https://t.me/c/123/2"), ("Jon Uik 3", "https://t.me/c/123/3"), ("Jon Uik 4", "https://t.me/c/123/4"), ("Forsaj 1", "https://t.me/c/123/5"), ("Forsaj 9", "https://t.me/c/123/6"), ("Forsaj 10", "https://t.me/c/123/7"), ("Dedpul", "https://t.me/c/123/8"), ("Gladiator", "https://t.me/c/123/9"), ("Top Gan", "https://t.me/c/123/10"), ("Betmen", "https://t.me/c/123/11"), ("Spiderman", "https://t.me/c/123/12"), ("Kingsman", "https://t.me/c/123/13"), ("Reaktiv", "https://t.me/c/123/14"), ("Transfomer", "https://t.me/c/123/15"), ("Rambo", "https://t.me/c/123/16"), ("Terminator", "https://t.me/c/123/17"), ("Ip Man", "https://t.me/c/123/18"), ("Mortal Kombat", "https://t.me/c/123/19"), ("Toshqin", "https://t.me/c/123/20")],
        "k_2": [("1+1", "link"), ("Maska", "link"), ("Uyda yolg'iz 1", "link"), ("Uyda yolg'iz 2", "link"), ("Janob Bin", "link"), ("Diktator", "link"), ("Ted", "link"), ("Oshpaz", "link"), ("Free Guy", "link"), ("Katta yigit", "link"), ("Oshpaz 2", "link"), ("Zoolander", "link"), ("Hangover", "link"), ("Bad Boys", "link"), ("Rush Hour", "link"), ("Minionlar", "link"), ("Shrek", "link"), ("Kung Fu Panda", "link"), ("Madagaskar", "link"), ("Muzlik davri", "link")],
        "k_3": [("Astral 1", "link"), ("Astral 2", "link"), ("Anabell", "link"), ("Chaqiriq", "link"), ("Nunn", "link"), ("Arr", "link"), ("IT", "link"), ("Vahima", "link"), ("Qabriston", "link"), ("Zulmat", "link"), ("Eksorsist", "link"), ("Saw X", "link"), ("Scream", "link"), ("Halloween", "link"), ("Sinister", "link"), ("Mama", "link"), ("Omen", "link"), ("The Ring", "link"), ("The Grudge", "link"), ("Us", "link")],
        "k_4": [("Avatar 1", "link"), ("Avatar 2", "link"), ("Interstellar", "link"), ("Tenet", "link"), ("Duna 1", "link"), ("Duna 2", "link"), ("Inception", "link"), ("Matrix", "link"), ("Marslik", "link"), ("Tor", "link"), ("Loki", "link"), ("Star Wars", "link"), ("Prometey", "link"), ("Aliens", "link"), ("Predator", "link"), ("Avengers", "link"), ("Iron Man", "link"), ("Black Panther", "link"), ("Doctor Strange", "link"), ("Guardians", "link")],
        "k_5": [("Titanik", "link"), ("Joker", "link"), ("Yashil mil", "link"), ("Sherlok", "link"), ("Otam", "link"), ("Parazit", "link"), ("Leon", "link"), ("Seven", "link"), ("Skarfeys", "link"), ("Lala Land", "link"), ("Hachiko", "link"), ("Pianist", "link"), ("The Whale", "link"), ("Braveheart", "link"), ("Troy", "link"), ("Elvis", "link"), ("Oppenheimer", "link"), ("Napoleon", "link"), ("Barbi", "link"), ("Gran Turismo", "link")],
        "k_6": [("Moana", "link"), ("Rio", "link"), ("Koko", "link"), ("Luka", "link"), ("Raya", "link"), ("Zootopiya", "link"), ("Up", "link"), ("Wall-E", "link"), ("Ratatuy", "link"), ("Cars 1", "link"), ("Cars 2", "link"), ("Cars 3", "link"), ("Toy Story", "link"), ("Soul", "link"), ("Encanto", "link"), ("Bambi", "link"), ("Lion King", "link"), ("Aladdin", "link"), ("Frozen", "link"), ("Tangled", "link")]
    }
    return movies.get(genre_key, [])

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📰 KUN.UZ YANGILIKLAR", "💰 VALYUTA", "🌤 OB-HAVO", "🎬 KINOLAR")
    bot.send_message(m.chat.id, f"Assalomu Alaykum! Bo'limni tanlang:", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def main_menu(m):
    txt = m.text.upper()
    if "KUN.UZ" in txt:
        try:
            r = requests.get("https://kun.uz/news/rss")
            soup = BeautifulSoup(r.content, 'xml')
            res = "".join([f"🔴 {i.title.text}\n🔗 [Ochish]({i.link.text})\n\n" for i in soup.find_all('item')[:10]])
            bot.send_message(m.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
        except: bot.send_message(m.chat.id, "⚠️ Xato yuz berdi.")

    elif "VALYUTA" in txt:
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            res = "💰 **VALYUTA KURSLARI (10 TA):**\n\n"
            for i in r[:10]:
                res += f"🔹 1 {i['Ccy']} = {i['Rate']} so'm\n"
            bot.send_message(m.chat.id, res)
        except: bot.send_message(m.chat.id, "⚠️ Ma'lumot yo'q.")

    elif "OB-HAVO" in txt:
        kb = types.InlineKeyboardMarkup(row_width=3)
        btns = [("Toshkent", "w_Tashkent"), ("Samarqand", "w_Samarkand"), ("Andijon", "w_Andijan"), ("Farg'ona", "w_Fergana"), ("Namangan", "w_Namangan"), ("Buxoro", "w_Bukhara"), ("Navoiy", "w_Navoi"), ("Qarshi", "w_Karshi"), ("Termiz", "w_Termez"), ("Nukus", "w_Nukus"), ("Guliston", "w_Guliston"), ("Jizzax", "w_Jizzakh"), ("Urgench", "w_Urgench")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in btns])
        bot.send_message(m.chat.id, "🌤 Viloyatni tanlang:", reply_markup=kb)

    elif "KINOLAR" in txt:
        kb = types.InlineKeyboardMarkup(row_width=2)
        j = [("🔥 Action", "k_1"), ("😂 Komediya", "k_2"), ("😱 Horror", "k_3"), ("🚀 Sci-Fi", "k_4"), ("🎭 Drama", "k_5"), ("👶 Multfilm", "k_6")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in j])
        bot.send_message(m.chat.id, "🎥 Janrni tanlang (Har birida 20 ta kino):", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, get_weather(call.data[2:]))
    elif call.data.startswith("k_"):
        m_list = get_movies(call.data)
        res = "🎬 **Kinolar Ro'yxati:**\n\n" + "\n".join([f"🔹 [{n}]({l})" for n, l in m_list])
        bot.send_message(call.message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    Thread(target=run).start()
    Thread(target=check_currency_update).start() # Eslatmani ishga tushirish
    bot.infinity_polling()
