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
        return res
    except: return ["⚠️ Kun.uz vaqtincha ishlamayapti."]

# 2. 10 ta Valyuta kursi (Markaziy Bank API)
def get_currency_10():
    try:
        r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        res = "💰 **Rasmiy valyuta kurslari (10 ta):**\n\n"
        # Eng ommabop 10 ta valyutani tanlab olamiz
        for i in range(10):
            name = r[i]['CcyNm_UZ']
            rate = r[i]['Rate']
            symbol = r[i]['Ccy']
            res += f"🔹 1 {symbol} ({name}) = {rate} so'm\n"
        return res
    except: return "⚠️ Valyuta kurslarini olib bo'lmadi."

# 3. Kengaytirilgan Sport/Futbol funksiyasi
def get_sport_news():
    sources = [
        {"name": "Championat.asia", "url": "https://championat.asia/uz/news/rss"},
        {"name": "Stadion.uz", "url": "https://stadion.uz/rss.php"}
    ]
    res = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for src in sources:
        try:
            r = requests.get(src['url'], headers=headers, timeout=10)
            root = ET.fromstring(r.content)
            # Har bir saytdan 3 tadan yangilik olamiz
            for item in root.findall('.//item')[:3]:
                title = item.find('title').text
                link = item.find('link').text
                res.append(f"⚽️ **{src['name']}**:\n{title}\n🔗 {link}")
        except: continue
    
    return res if res else ["⚠️ Sport yangiliklarini olib bo'lmadi."]

# 4. Ob-havo ma'lumotlari (Statik ro'yxat)
weather_data = {
    "toshkent": "🌤 Toshkent: +12°C", "samarqand": "☁️ Samarqand: +10°C",
    "andijon": "⛅️ Andijon: +13°C", "fargona": "☀️ Farg'ona: +14°C",
    "namangan": "🌤 Namangan: +12°C", "buxoro": "☀️ Buxoro: +16°C",
    "navoiy": "☀️ Navoiy: +15°C", "qarshi": "🌤 Qarshi: +17°C",
    "termiz": "☀️ Termiz: +20°C", "nukus": "☁️ Nukus: +5°C",
    "guliston": "🌤 Guliston: +11°C", "jizzax": "⛅️ Jizzax: +12°C",
    "urganch": "☁️ Urganch: +7°C"
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🔵 Kun.uz", callback_data="kunuz")
    btn2 = types.InlineKeyboardButton("🏆 Sport/Futbol", callback_data="sport")
    btn3 = types.InlineKeyboardButton("💰 10 ta Valyuta", callback_data="currency")
    btn4 = types.InlineKeyboardButton("🌤 Viloyatlar Ob-havosi", callback_data="weather_menu")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "kunuz":
        bot.send_message(call.message.chat.id, "\n\n".join(get_kun_uz()))
    elif call.data == "sport":
        bot.send_message(call.message.chat.id, "\n\n".join(get_sport_news()))
    elif call.data == "currency":
        bot.send_message(call.message.chat.id, get_currency_10(), parse_mode="Markdown")
    elif call.data == "weather_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(v.capitalize(), callback_data=f"w_{v}") for v in weather_data.keys()]
        markup.add(*buttons)
        bot.edit_message_text("Viloyatni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith("w_"):
        shahar = call.data.replace("w_", "")
        bot.send_message(call.message.chat.id, weather_data[shahar])

bot.polling(none_stop=True)


