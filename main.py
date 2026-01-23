import requests, telebot, os
from telebot import types
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# 1. RENDER PORT MUAMMOSINI YECHISH
app = Flask('')
@app.route('/')
def home(): return "Bot ishlayapti!"

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8468486478:AAEpNjWEFzVr6cuwrhNaDMIfHRi1rS7Jn6Y"
bot = telebot.TeleBot(TOKEN)

# 2. OB-HAVO (API orqali)
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=b713020054700d98192801e0e8e97495&units=metric&lang=uz"
        r = requests.get(url, timeout=10).json()
        return f"📍 **{city.upper()}**\n🌡 Harorat: {r['main']['temp']}°C\n☁️ {r['weather'][0]['description'].capitalize()}"
    except: return "⚠️ Ob-havo ma'lumoti topilmadi."

# 3. KINOLAR BAZASI
movies = {
    "k_1": [("Jon Uik 4", "https://uzmovi.com/search?q=John+Wick"), ("Forsaj 10", "https://uzmovi.com/search?q=Fast")],
    "k_2": [("1+1", "https://uzmovi.com/search?q=Intouchables"), ("Maska", "https://uzmovi.com/search?q=Mask")],
    "k_3": [("Astral", "https://uzmovi.com/search?q=Insidious"), ("Anabell", "https://uzmovi.com/search?q=Annabelle")],
    "k_4": [("Avatar", "https://uzmovi.com/search?q=Avatar"), ("O'rgimchak odam", "https://uzmovi.com/search?q=Spider")],
    "k_5": [("Titanik", "https://uzmovi.com/search?q=Titanic"), ("Joker", "https://uzmovi.com/search?q=Joker")],
    "k_6": [("Shrek", "https://uzmovi.com/search?q=Shrek"), ("Moana", "https://uzmovi.com/search?q=Moana")]
}

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📰 So'nggi Yangiliklar", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    bot.send_message(m.chat.id, "Bot Web Servisda muvaffaqiyatli yoqildi! ✅", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle_menu(m):
    if m.text == "📰 So'nggi Yangiliklar":
        try:
            r = requests.get("https://kun.uz/news/rss")
            soup = BeautifulSoup(r.content, 'xml')
            res = "".join([f"🔴 {i.title.text}\n🔗 [Ochish]({i.link.text})\n\n" for i in soup.find_all('item')[:10]])
            bot.send_message(m.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
        except: bot.send_message(m.chat.id, "⚠️ Yangiliklar yuklanmadi.")
    elif m.text == "💰 Valyuta":
        r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        res = "💰 **Valyuta:**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
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
def callback_handler(call):
    if call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, get_weather(call.data[2:]), parse_mode="Markdown")
    elif call.data.startswith("k_"):
        res = "🎬 **Kinolar:**\n\n" + "\n".join([f"🔹 [{n}]({l})" for n, l in movies[call.data]])
        bot.send_message(call.message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
