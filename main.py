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

TOKEN = "8468486478:AAGzmOlFP5TWGUB5CzffN4wbNDHv77zfKUc"
bot = telebot.TeleBot(TOKEN)

# 1. Kun.uz funksiyasi
def get_kun_uz():
    url = "https://kun.uz/news/rss"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        root = ET.fromstring(r.content)
        res = []
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text
            link = item.find('link').text
            res.append(f"🔵 {title}\n🔗 {link}")
        return res if res else ["⚠️ Kun.uz RSS manbasi bo'sh."]
    except Exception as e:
        return [f"⚠️ Kun.uz RSS xatosi: {e}"]

# 2. Daryo.uz funksiyasi (Kun.uz bilan bir xil qilindi)
def get_daryo_uz():
    url = "https://daryo.uz/feed/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        root = ET.fromstring(r.content)
        res = []
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text
            link = item.find('link').text
            res.append(f"🔴 {title}\n🔗 {link}")
        return res if res else ["⚠️ Daryo.uz RSS manbasi bo'sh."]
    except Exception as e:
        return [f"⚠️ Daryo RSS xatosi: {e}"]

# 3. Start va Tugmalar
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🔵 Kun.uz", callback_data="kunuz")
    btn2 = types.InlineKeyboardButton("🔴 Daryo.uz", callback_data="daryouz")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Qaysi saytdan yangilik o'qiymiz?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "kunuz":
        news = get_kun_uz()
        title_text = "📢 KUN.UZ YANGILIKLARI:"
    elif call.data == "daryouz":
        news = get_daryo_uz()
        title_text = "📢 DARYO.UZ YANGILIKLARI:"

    response = f"**{title_text}**\n\n"
    for i, n in enumerate(news, 1):
        response += f"{i}. {n}\n\n"
    
    bot.send_message(call.message.chat.id, response, parse_mode="Markdown")

bot.polling(none_stop=True)
