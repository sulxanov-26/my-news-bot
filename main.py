import requests
from bs4 import BeautifulSoup
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

# Botni ishga tushirishdan oldin serverni yoqish
keep_alive()

# Sizning Telegram tokeningiz joylangan holatda
TOKEN = "8468486478:AAGzmOlFP5TWGUB5CzfFN4wbNDHv77zfkUc"
bot = telebot.TeleBot(TOKEN)

# 1. Kun.uz funksiyasi
import xml.etree.ElementTree as ET

def get_kun_uz():
    # Kun.uz-ning rasmiy RSS manbasi
    url = "https://kun.uz/news/rss"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        # XML ma'lumotini o'qiymiz
        root = ET.fromstring(r.content)
        res = []
        
        # RSS ichidagi yangiliklarni qidiramiz
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text
            link = item.find('link').text
            res.append(f"🔵 {title}\n🔗 {link}")
            
        return res if res else ["⚠️ Kun.uz RSS manbasi bo'sh."]
    except Exception as e:
        return [f"⚠️ RSS xatosi: {e}"]




# 2. Daryo.uz funksiyasi
def get_daryo_uz():
    # Eng barqaror manzil - bu asosiy feed
    url = "https://daryo.uz/feed/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        import re
        # Sarlavhalar va linklarni qidirish (Regex - eng chidamlisi)
        titles = re.findall(r'<title>(.*?)</title>', r.text)
        links = re.findall(r'<link>(.*?)</link>', r.text)

        # Agar manba rostdan ham bo'sh bo'lsa (faqat sayt nomi bo'lsa)
        if len(titles) <= 1:
            return ["⚠️ Daryo.uz serveri hozir yangilik bermayapti. Birozdan so'ng urinib ko'ring."]

        res = []
        # Kun.uz kabi 5 ta yangilikni tayyorlash
        for i in range(1, min(6, len(titles))):
            t = titles[i].replace('<![CDATA[', '').replace(']]>', '').strip()
            l = links[i].strip() if i < len(links) else ""
            if t: # Bo'sh bo'lmagan sarlavhalarni qo'shish
                res.append(f"🔴 {t}\n🔗 {l}")
        
        return res
    except Exception as e:
        return [f"⚠️ Daryo RSS xatosi: {e}"]








# 3. Start va Tugmalar
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔵 Kun.uz")
    btn2 = types.KeyboardButton("🔴 Daryo.uz")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Qaysi saytdan yangilik o'qiymiz?", reply_markup=markup)

# 4. Tanlovga qarab javob berish
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "🔵 Kun.uz":
        news = get_kun_uz()
        text = "📢 *KUN.UZ YANGILIKLARI:*\n\n" + "\n\n".join([f"{i+1}. {n}" for i, n in enumerate(news)])
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
        
    elif message.text == "🔴 Daryo.uz":
        news = get_daryo_uz()
        text = "📢 *DARYO.UZ YANGILIKLARI:*\n\n" + "\n\n".join([f"{i+1}. {n}" for i, n in enumerate(news)])
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

print("Bot serverda ishga tushdi...")
bot.infinity_polling()
