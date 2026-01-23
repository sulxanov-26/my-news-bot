import requests
import telebot
from telebot import types
from bs4 import BeautifulSoup
import os

TOKEN = "8468486478:AAGiRCO0RAolKaY2FYSWKyjO2aCh9iu-k9Y"
bot = telebot.TeleBot(TOKEN)

# OB-HAVO (Faqat hozirgi harorat va holat)
def get_weather(city):
    try:
        # Hozirgi holatni olish uchun barqaror API
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=b713020054700d98192801e0e8e97495&units=metric&lang=uz"
        r = requests.get(url, timeout=10).json()
        gradus = r['main']['temp']
        holat = r['weather'][0]['description']
        return f"📍 **{city.upper()}**\n\n🌡 Harorat: {gradus}°C\n☁️ Holat: {holat.capitalize()}"
    except:
        return "⚠️ Ob-havo ma'lumotini yuklashda xatolik."

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📰 So'nggi Yangiliklar", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    bot.send_message(m.chat.id, "Assalomu Alaykum Profil egasi 👋\n\nMarhamat Menyuni tanlang: 👇", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle_menu(m):
    if m.text == "📰 So'nggi Yangiliklar":
        try:
            r = requests.get("https://kun.uz/news/rss", timeout=10)
            soup = BeautifulSoup(r.content, 'xml')
            items = soup.find_all('item')[:10]
            res = ""
            for i in items:
                res += f"🔴 {i.title.text}\n🔗 [Ochish]({i.link.text})\n\n"
            bot.send_message(m.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
        except:
            bot.send_message(m.chat.id, "⚠️ Kun.uz yangiliklarini olib bo'lmadi.")

    elif m.text == "💰 Valyuta":
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            res = "💰 **Valyuta kurslari (MB):**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
            bot.send_message(m.chat.id, res)
        except:
            bot.send_message(m.chat.id, "⚠️ Valyuta kurslarini yuklab bo'lmadi.")

    elif m.text == "🌤 Ob-havo":
        kb = types.InlineKeyboardMarkup(row_width=3)
        cities = [("Toshkent", "Tashkent"), ("Samarqand", "Samarkand"), ("Andijon", "Andijan"), ("Farg'ona", "Fergana"), ("Namangan", "Namangan"), ("Buxoro", "Bukhara"), ("Navoiy", "Navoi"), ("Qarshi", "Karshi"), ("Termiz", "Termez"), ("Guliston", "Guliston"), ("Jizzax", "Jizzakh"), ("Urganch", "Urgench"), ("Nukus", "Nukus")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=f"w_{d}") for t, d in cities])
        bot.send_message(m.chat.id, "🌤 Viloyatni tanlang:", reply_markup=kb)

    elif m.text == "🎬 Kinolar":
        kb = types.InlineKeyboardMarkup(row_width=2)
        janrlar = [("🔥 Jangovar", "k_1"), ("😂 Komediya", "k_2"), ("😱 Qo'rqinchli", "k_3"), ("🚀 Fantastika", "k_4"), ("🎭 Drama", "k_5"), ("👶 Multfilm", "k_6")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in janrlar])
        bot.send_message(m.chat.id, "🎥 Janrni tanlang:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, get_weather(call.data[2:]), parse_mode="Markdown")
    elif call.data.startswith("k_"):
        # Har bir janr uchun 10 tadan film ro'yxati
        res = "🎬 **TOP 10 Film:**\n\n" + "\n".join([f"{i}. [Kino linki {i}](https://uzmovi.com/search?q=film)" for i in range(1, 11)])
        bot.send_message(call.message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

bot.polling(none_stop=True)

