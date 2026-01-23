import requests, telebot, os
from telebot import types
from flask import Flask
from threading import Thread

# 1. RENDER WEB SERVICE PORTINI OCHISH
app = Flask('')
@app.route('/')
def home(): return "Bot Muvaffaqiyatli Ishlayapti! ✅"

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8468486478:AAEpNjWEFzVr6cuwrhNaDMIfHRi1rS7Jn6Y"
bot = telebot.TeleBot(TOKEN)

# 2. OB-HAVO FUNKSIYASI (API - SIZ SO'RAGAN FORMATDA)
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=b713020054700d98192801e0e8e97495&units=metric&lang=uz"
        r = requests.get(url, timeout=10).json()
        temp = r['main']['temp']
        desc = r['weather'][0]['description']
        return f"📍 **{city}**: {temp}°C, {desc.capitalize()}"
    except:
        return "⚠️ Ma'lumot topilmadi."

# 3. KINOLAR BAZASI (6 JANR X 10 TA FILM)
movies_data = {
    "k_1": [("Jon Uik 4", "https://uzmovi.com/filmlar/john-wick-4"), ("Forsaj 10", "https://uzmovi.com/filmlar/fast-x"), ("Dedpul", "https://uzmovi.com/filmlar/deadpool"), ("Gladiator", "https://uzmovi.com/filmlar/gladiator"), ("Top Gan", "https://uzmovi.com/filmlar/top-gun"), ("Betmen", "https://uzmovi.com/filmlar/the-batman"), ("Spiderman", "https://uzmovi.com/filmlar/spider-man"), ("Kingsman", "https://uzmovi.com/filmlar/kingsman"), ("Reaktiv", "https://uzmovi.com/filmlar/extraction"), ("Transfomer", "https://uzmovi.com/filmlar/transformers")],
    "k_2": [("1+1", "https://uzmovi.com/filmlar/the-intouchables"), ("Maska", "https://uzmovi.com/filmlar/the-mask"), ("Uyda yolg'iz", "https://uzmovi.com/filmlar/home-alone"), ("Janob Bin", "https://uzmovi.com/filmlar/mr-bean"), ("Diktator", "https://uzmovi.com/filmlar/the-dictator"), ("Ted", "https://uzmovi.com/filmlar/ted"), ("Oshpaz", "https://uzmovi.com/filmlar/chef"), ("Free Guy", "https://uzmovi.com/filmlar/free-guy"), ("Katta yigit", "https://uzmovi.com/filmlar/big"), ("Oshpaz-2", "https://uzmovi.com/filmlar/chef-2")],
    "k_3": [("Astral", "https://uzmovi.com/filmlar/insidious"), ("Anabell", "https://uzmovi.com/filmlar/annabelle"), ("Chaqiriq", "https://uzmovi.com/filmlar/the-conjuring"), ("Nunn", "https://uzmovi.com/filmlar/the-nun"), ("Arr", "https://uzmovi.com/filmlar/saw"), ("IT", "https://uzmovi.com/filmlar/it"), ("Zulmat", "https://uzmovi.com/filmlar/lights-out"), ("Tungi ov", "https://uzmovi.com/filmlar/night-hunt"), ("Qabriston", "https://uzmovi.com/filmlar/cemetery"), ("Vahima", "https://uzmovi.com/filmlar/panic")],
    "k_4": [("Avatar", "https://uzmovi.com/filmlar/avatar"), ("Tor", "https://uzmovi.com/filmlar/thor"), ("Marslik", "https://uzmovi.com/filmlar/the-martian"), ("Interstellar", "https://uzmovi.com/filmlar/interstellar"), ("Tenet", "https://uzmovi.com/filmlar/tenet"), ("Duna", "https://uzmovi.com/filmlar/dune"), ("Inception", "https://uzmovi.com/filmlar/inception"), ("Matrix", "https://uzmovi.com/filmlar/the-matrix"), ("Prometey", "https://uzmovi.com/filmlar/prometheus"), ("Star Wars", "https://uzmovi.com/filmlar/star-wars")],
    "k_5": [("Titanik", "https://uzmovi.com/filmlar/titanic"), ("Joker", "https://uzmovi.com/filmlar/joker"), ("Yashil mil", "https://uzmovi.com/filmlar/the-green-mile"), ("Sherlok", "https://uzmovi.com/filmlar/sherlock"), ("Otam", "https://uzmovi.com/filmlar/the-father"), ("Lala Land", "https://uzmovi.com/filmlar/la-la-land"), ("Parazit", "https://uzmovi.com/filmlar/parasite"), ("Leon", "https://uzmovi.com/filmlar/leon"), ("Skarfeys", "https://uzmovi.com/filmlar/scarface"), ("Yetti", "https://uzmovi.com/filmlar/seven")],
    "k_6": [("Shrek", "https://uzmovi.com/filmlar/shrek"), ("Moana", "https://uzmovi.com/filmlar/moana"), ("Kung-fu Panda", "https://uzmovi.com/filmlar/kung-fu-panda"), ("Rio", "https://uzmovi.com/filmlar/rio"), ("Muzlik davri", "https://uzmovi.com/filmlar/ice-age"), ("Madagaskar", "https://uzmovi.com/filmlar/madagascar"), ("Koko", "https://uzmovi.com/filmlar/coco"), ("Luka", "https://uzmovi.com/filmlar/luca"), ("Raya", "https://uzmovi.com/filmlar/raya"), ("Zootopiya", "https://uzmovi.com/filmlar/zootopia")]
}

@bot.message_handler(commands=['start'])
def start(m):
    name = m.from_user.first_name
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📰 So'nggi Yangiliklar", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    bot.send_message(m.chat.id, f"Assalomu Alaykum **{name}**!\n\nMarhamat kerakli bo'limni tanlang:", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def menu(m):
    if m.text == "📰 So'nggi Yangiliklar":
        try:
            r = requests.get("https://kun.uz/news/rss")
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.content, 'xml')
            res = "".join([f"🔴 {i.title.text}\n🔗 [Ochish]({i.link.text})\n\n" for i in soup.find_all('item')[:10]])
            bot.send_message(m.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
        except: bot.send_message(m.chat.id, "⚠️ Yangiliklar yuklanmadi.")
    elif m.text == "💰 Valyuta":
        r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        res = "💰 **Valyuta kursi:**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
        bot.send_message(m.chat.id, res)
    elif m.text == "🌤 Ob-havo":
        kb = types.InlineKeyboardMarkup(row_width=3)
        c = [("Toshkent", "Tashkent"), ("Samarqand", "Samarkand"), ("Andijon", "Andijan"), ("Farg'ona", "Fergana"), ("Namangan", "Namangan"), ("Buxoro", "Bukhara"), ("Navoiy", "Navoi"), ("Qarshi", "Karshi"), ("Termiz", "Termez"), ("Guliston", "Guliston"), ("Jizzax", "Jizzakh"), ("Urganch", "Urgench"), ("Nukus", "Nukus")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=f"w_{d}") for t, d in c])
        bot.send_message(m.chat.id, "🌤 Viloyatni tanlang:", reply_markup=kb)
    elif m.text == "🎬 Kinolar":
        kb = types.InlineKeyboardMarkup(row_width=2)
        j = [("🔥 Jangovar", "k_1"), ("😂 Komediya", "k_2"), ("😱 Qo'rqinchli", "k_3"), ("🚀 Fantastika", "k_4"), ("🎭 Drama", "k_5"), ("👶 Multfilm", "k_6")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in j])
        bot.send_message(m.chat.id, "🎥 Janrni tanlang:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, get_weather(call.data[2:]), parse_mode="Markdown")
    elif call.data.startswith("k_"):
        genre = {"k_1":"Jangovar","k_2":"Komediya","k_3":"Qo'rqinchli","k_4":"Fantastika","k_5":"Drama","k_6":"Multfilm"}[call.data]
        res = f"🎬 **{genre} janridagi TOP 10 film:**\n\n"
        for name, link in movies_data[call.data]:
            res += f"🔹 [{name}]({link})\n"
        bot.send_message(call.message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
