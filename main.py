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

TOKEN = "8468486478:AAEQOVdLYDAf42lthIgBibw1Whz-YiR8XYc"
bot = telebot.TeleBot(TOKEN)

# ASOSIY MENYU (Endi 5 ta tugma)
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🔵 Kun.uz")
    btn2 = types.KeyboardButton("🏆 Sport/Futbol")
    btn3 = types.KeyboardButton("💰 Valyuta")
    btn4 = types.KeyboardButton("🌤 Ob-havo")
    btn5 = types.KeyboardButton("🎬 Kinolar") # Yangi menyu
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# 1. Sport funksiyasi (6 ta manba)
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
    return res

# 2. Yangi Kinolar funksiyasi
def get_movies():
    # Bu yerda misol tariqasida mashhur kinolar ro'yxati
    movies = [
        "🎬 **Avatar: Suv yo'li**\n⭐️ Reyting: 7.8\n🎭 Janr: Fantastika",
        "🎬 **Oppenheimer**\n⭐️ Reyting: 8.4\n🎭 Janr: Tarixiy/Drama",
        "🎬 **Barbie**\n⭐️ Reyting: 7.0\n🎭 Janr: Komediya",
        "🎬 **Napoleon**\n⭐️ Reyting: 6.7\n🎭 Janr: Jangovar"
    ]
    return movies

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot yangilandi! Pastdan bo'limni tanlang:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "🔵 Kun.uz":
        bot.send_message(message.chat.id, "🔵 So'nggi yangiliklar:")
        # Kun.uz funksiyasi chaqiriladi
    elif message.text == "🏆 Sport/Futbol":
        bot.send_message(message.chat.id, "⌛️ Sport xabarlari yuklanmoqda...")
        news = get_sport_news()
        bot.send_message(message.chat.id, "\n\n".join(news))
    elif message.text == "💰 Valyuta":
        # Valyuta funksiyasi chaqiriladi
        bot.send_message(message.chat.id, "💰 Valyuta kurslari yangilanmoqda...")
    elif message.text == "🎬 Kinolar":
        movies = get_movies()
        bot.send_message(message.chat.id, "🍿 **Hozirda mashhur kinolar:**\n\n" + "\n\n".join(movies))
    elif message.text == "🌤 Ob-havo":
        # Ob-havo menyusi chaqiriladi
        bot.send_message(message.chat.id, "Viloyatni tanlang:")

bot.polling(none_stop=True)



