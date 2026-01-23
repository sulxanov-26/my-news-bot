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

# 3. Start va Tugmalar
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🔵 Kun.uz Yangiliklari", callback_data="kunuz")
    markup.add(btn1)
    bot.send_message(message.chat.id, "Salom! Kun.uz yangiliklarini o'qish uchun pastdagi tugmani bosing:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "kunuz":
        news = get_kun_uz()
        response = "📢 **KUN.UZ YANGILIKLARI:**\n\n"
        for i, n in enumerate(news, 1):
            response += f"{i}. {n}\n\n"
        bot.send_message(call.message.chat.id, response, parse_mode="Markdown")

bot.polling(none_stop=True)

