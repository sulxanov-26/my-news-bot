import requests
import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread
import xml.etree.ElementTree as ET

# 1. Server qismi (Render uchun)
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# 2. Bot sozlamalari
TOKEN = "8468486478:AAEQOVdLYDAf42lthIgBibw1Whz-YiR8XYc"
bot = telebot.TeleBot(TOKEN)

# 3. Asosiy Menyular
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🔵 Kun.uz", "🏆 Sport/Futbol", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    return markup

def weather_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    regions = ["Toshkent", "Samarqand", "Andijon", "Farg'ona", "Namangan", "Buxoro", "Navoiy", "Qarshi", "Termiz", "Nukus", "Guliston", "Jizzax", "Urganch"]
    btns = [types.InlineKeyboardButton(v, callback_data=f"w_{v.lower()}") for v in regions]
    markup.add(*btns)
    return markup

# 4. Funksiyalar (Ma'lumot olish)
def get_kun_uz():
    try:
        r = requests.get("https://kun.uz/news/rss", timeout=10)
        root = ET.fromstring(r.content)
        return [f"🔵 {i.find('title').text}\n🔗 {i.find('link').text}" for i in root.findall('.//item')[:5]]
    except: return ["⚠️ Kun.uz yangiliklarini olib bo'lmadi."]

def get_currency():
    try:
        r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        res = "💰 **Rasmiy valyuta kurslari:**\n\n"
        for i in range(10):
            res += f"🔹 1 {r[i]['Ccy']} ({r[i]['CcyNm_UZ']}) = {r[i]['Rate']} so'm\n"
        return res
    except: return "⚠️ Valyuta kurslarini olib bo'lmadi."

def get_sport_news():
    sources = [
        {"name": "Tribuna.uz", "url": "https://kun.uz/news/category/sport/rss"},
        {"name": "Championat.asia", "url": "https://championat.asia/uz/news/rss"},
        {"name": "Stadion.uz", "url": "https://stadion.uz/rss.php"}
    ]
    res = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for src in sources:
        try:
            r = requests.get(src['url'], headers=headers, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:2]:
                res.append(f"⚽️ **{src['name']}**:\n{item.find('title').text}\n🔗 {item.find('link').text}")
        except: continue
    return res if res else ["⚠️ Sport yangiliklari vaqtincha band."]

def get_movies():
    return [
        "🎬 **Avatar: Suv yo'li**\n⭐️ Reyting: 7.8\n🎭 Janr: Fantastika",
        "🎬 **Oppenheimer**\n⭐️ Reyting: 8.4\n🎭 Janr: Tarixiy",
        "🎬 **Napoleon**\n⭐️ Reyting: 6.7\n🎭 Janr: Jangovar",
        "🎬 **Qora Pantera 2**\n⭐️ Reyting: 7.2\n🎭 Janr: Marvel"
    ]

# 5. Buyruqlarni boshqarish
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot hamma funksiyalari bilan tayyor! Tanlang:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "🔵 Kun.uz":
        bot.send_message(message.chat.id, "🔵 So'nggi yangiliklar:\n\n" + "\n\n".join(get_kun_uz()))
    elif message.text == "🏆 Sport/Futbol":
        bot.send_message(message.chat.id, "⌛️ 3 ta manbadan xabarlar yuklanmoqda...")
        news = get_sport_news()
        bot.send_message(message.chat.id, "\n\n".join(news))
    elif message.text == "💰 Valyuta":
        bot.send_message(message.chat.id, get_currency(), parse_mode="Markdown")
    elif message.text == "🎬 Kinolar":
        bot.send_message(message.chat.id, "🍿 **Hozirda mashhur kinolar:**\n\n" + "\n\n".join(get_movies()))
    elif message.text == "🌤 Ob-havo":
        bot.send_message(message.chat.id, "Viloyatni tanlang:", reply_markup=weather_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    weather_info = {
        "w_toshkent": "🌤 Toshkent: +12°C", "w_samarqand": "☁️ Samarqand: +10°C", "w_andijon": "⛅️ Andijon: +13°C",
        "w_farg'ona": "☀️ Farg'ona: +14°C", "w_namangan": "🌤 Namangan: +12°C", "w_buxoro": "☀️ Buxoro: +16°C",
        "w_navoiy": "☀️ Navoiy: +15°C", "w_qarshi": "🌤 Qarshi: +17°C", "w_termiz": "☀️ Termiz: +20°C",
        "w_nukus": "☁️ Nukus: +5°C", "w_guliston": "🌤 Guliston: +11°C", "w_jizzax": "⛅️ Jizzax: +12°C", "w_urganch": "☁️ Urganch: +7°C"
    }
    if call.data in weather_info:
        bot.send_message(call.message.chat.id, weather_info[call.data], reply_markup=main_menu())
        bot.answer_callback_query(call.id)

# 6. Botni ishga tushirish
bot.polling(none_stop=True)


