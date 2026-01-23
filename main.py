import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread
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
TOKEN = "8468486478:AAES1NzEb0bwTL3zGxD_FpBMDlVqrdx2w2k"
bot = telebot.TeleBot(TOKEN)

# 1. Kun.uz funksiyasi
def get_kun_uz():
    url = "https://kun.uz/news/list"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Kun.uz-ning yangiliklar bloklarini qidiramiz
        links = soup.find_all('a', class_='daily-block l-item')
        
        res = []
        for link in links[:5]: # Eng oxirgi 5 ta yangilik
            title = link.find('span', class_='news-title')
            if title:
                text = title.get_text(strip=True)
                href = "https://kun.uz" + link.get('href')
                res.append(f"🔵 {text}\n🔗 {href}")
        
        # Agar yangilik topilmasa, eski klassni tekshirib ko'ramiz
        if not res:
            links = soup.find_all('a', class_='news__title')
            for link in links[:5]:
                text = link.get_text(strip=True)
                href = "https://kun.uz" + link.get('href')
                res.append(f"🔵 {text}\n🔗 {href}")

        return res if res else ["⚠️ Hozircha yangilik topilmadi"]
    except Exception as e:
        return [f"⚠️ Xato yuz berdi: {e}"]


# 2. Daryo.uz funksiyasi
def get_daryo_uz():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get("https://daryo.uz/cyrillic/", headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        titles = soup.find_all(['h2', 'h3'], limit=15)
        res = [t.get_text(strip=True) for t in titles if len(t.get_text()) > 20]
        return res[:10]
    except: return ["⚠️ Daryo.uz dan ma'lumot olib bo'lmadi"]

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
