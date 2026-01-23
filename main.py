import requests
import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread
import xml.etree.ElementTree as ET

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# Tokeningiz
TOKEN = "8468486478:AAEQOVdLYDAf42lthIgBibw1Whz-YiR8XYc"
bot = telebot.TeleBot(TOKEN)

# ASOSIY MENYU (Pastki qismda turadigan doimiy tugmalar)
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🔵 Kun.uz")
    btn2 = types.KeyboardButton("🏆 Sport/Futbol")
    btn3 = types.KeyboardButton("💰 Valyuta")
    btn4 = types.KeyboardButton("🌤 Ob-havo")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# OB-HAVO VILOYATLAR MENYUSI (Xabar ichidagi tugmalar)
def weather_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    weather_data = ["Toshkent", "Samarqand", "Andijon", "Farg'ona", "Namangan", "Buxoro", "Navoiy", "Qarshi", "Termiz", "Nukus", "Guliston", "Jizzax", "Urganch"]
    buttons = [types.InlineKeyboardButton(v, callback_data=f"w_{v.lower()}") for v in weather_data]
    markup.add(*buttons)
    return markup

# 1. Kun.uz funksiyasi
def get_kun_uz():
    url = "https://kun.uz/news/rss"
    try:
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.content)
        res = []
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text
            link = item.find('link').text
            res.append(f"🔵 {title}\n🔗 {link}")
        return res
    except: return ["⚠️ Kun.uz yangiliklarini olib bo'lmadi."]

# 2. Valyuta kursi (10 ta)
def get_currency():
    try:
        r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        res = "💰 **Rasmiy valyuta kurslari:**\n\n"
        for i in range(10):
            res += f"🔹 1 {r[i]['Ccy']} ({r[i]['CcyNm_UZ']}) = {r[i]['Rate']} so'm\n"
        return res
    except: return "⚠️ Valyuta kurslarini olib bo'lmadi."

# 3. Sport yangiliklari (Yaxshilangan)
def get_sport_news():
    sources = [
        {"name": "Championat.asia", "url": "https://championat.asia/uz/news/rss"},
        {"name": "Tribuna.uz", "url": "https://kun.uz/news/category/sport/rss"}
    ]
    res = []
    for src in sources:
        try:
            r = requests.get(src['url'], timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:3]:
                title = item.find('title').text
                link = item.find('link').text
                res.append(f"⚽️ **{src['name']}**:\n{title}\n🔗 {link}")
        except: continue
    return res if res else ["⚠️ Sport yangiliklari hozirda band."]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot ishga tushdi! Kerakli bo'limni pastdan tanlang:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "🔵 Kun.uz":
        bot.send_message(message.chat.id, "\n\n".join(get_kun_uz()))
    elif message.text == "🏆 Sport/Futbol":
        bot.send_message(message.chat.id, "\n\n".join(get_sport_news()))
    elif message.text == "💰 Valyuta":
        bot.send_message(message.chat.id, get_currency(), parse_mode="Markdown")
    elif message.text == "🌤 Ob-havo":
        bot.send_message(message.chat.id, "Viloyatni tanlang:", reply_markup=weather_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    weather_info = {
        "w_toshkent": "🌤 Toshkent: +12°C", "w_samarqand": "☁️ Samarqand: +10°C",
        "w_andijon": "⛅️ Andijon: +13°C", "w_farg'ona": "☀️ Farg'ona: +14°C",
        "w_namangan": "🌤 Namangan: +12°C", "w_buxoro": "☀️ Buxoro: +16°C",
        "w_navoiy": "☀️ Navoiy: +15°C", "w_qarshi": "🌤 Qarshi: +17°C",
        "w_termiz": "☀️ Termiz: +20°C", "w_nukus": "☁️ Nukus: +5°C",
        "w_guliston": "🌤 Guliston: +11°C", "w_jizzax": "⛅️ Jizzax: +12°C",
        "w_urganch": "☁️ Urganch: +7°C"
    }
    if call.data in weather_info:
        bot.send_message(call.message.chat.id, weather_info[call.data])
        # Asosiy menyu (ReplyKeyboard) o'z-o'zidan pastda turaveradi

bot.polling(none_stop=True)



