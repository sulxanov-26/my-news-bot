import requests, telebot, os
from telebot import types
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# 1. RENDER UCHUN PORT MUAMMOSINI YECHISH (O'chirmang!)
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlashda davom etmoqda..."

def run_server():
    # Render avtomatik beradigan PORTni ushlab oladi
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8468486478:AAEQOVdLYDAf42lthIgBibw1Whz-YiR8XYc"
bot = telebot.TeleBot(TOKEN)

# 2. OB-HAVO (Bloklanmaydigan va Gradusni ko'rsatadigan API)
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=b713020054700d98192801e0e8e97495&units=metric&lang=uz"
        r = requests.get(url, timeout=10).json()
        temp = r['main']['temp']
        desc = r['weather'][0]['description']
        return f"📍 **{city.upper()}**\n\n🌡 Harorat: {temp}°C\n☁️ Holat: {desc.capitalize()}"
    except:
        return "⚠️ Ob-havo ma'lumotini yuklab bo'lmadi."

# 3. KINOLAR BAZASI (Nomlar va Linklar bilan)
movies_data = {
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
    bot.send_message(m.chat.id, "Assalomu Alaykum! Barcha muammolar tuzatildi. ✅", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle_text(m):
    if m.text == "📰 So'nggi Yangiliklar":
        try:
            r = requests.get("https://kun.uz/news/rss")
            soup = BeautifulSoup(r.content, 'xml')
            items = soup.find_all('item')[:10]
            res = ""
            for i in items:
                res += f"🔴 {i.title.text}\n🔗 [Ochish]({i.link.text})\n\n"
            bot.send_message(m.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
        except:
            bot.send_message(m.chat.id, "⚠️ Yangiliklar yuklanmadi.")

    elif m.text == "💰 Valyuta":
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            res = "💰 **Valyuta kursi (MB):**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
            bot.send_message(m.chat.id, res)
        except:
            bot.send_message(m.chat.id, "⚠️ Valyuta sayti band.")

    elif m.text == "🌤 Ob-havo":
        kb = types.InlineKeyboardMarkup(row_width=3)
        cities = [("Toshkent", "Tashkent"), ("Samarqand", "Samarkand"), ("Andijon", "Andijan"), ("Farg'ona", "Fergana"), ("Namangan", "Namangan"), ("Buxoro", "Bukhara"), ("Navoiy", "Navoi"), ("Qarshi", "Karshi"), ("Termiz", "Termez"), ("Guliston", "Guliston"), ("Jizzax", "Jizzakh"), ("Urganch", "Urgench"), ("Nukus", "Nukus")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=f"w_{d}") for t, d in cities])
        bot.send_message(m.chat.id, "🌤 Viloyatni tanlang:", reply_markup=kb)

    elif m.text == "🎬 Kinolar":
        kb = types.InlineKeyboardMarkup(row_width=2)
        j = [("🔥 Jangovar", "k_1"), ("😂 Komediya", "k_2"), ("😱 Qo'rqinchli", "k_3"), ("🚀 Fantastika", "k_4"), ("🎭 Drama", "k_5"), ("👶 Multfilm", "k_6")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in j])
        bot.send_message(m.chat.id, "🎥 Janrni tanlang:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, get_weather(call.data[2:]), parse_mode="Markdown")
    elif call.data.startswith("k_"):
        res = "🎬 **Siz tanlagan janr bo'yicha kinolar:**\n\n"
        for name, link in movies_data[call.data]:
            res += f"🔹 [{name}]({link})\n"
        bot.send_message(call.message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

# 4. BOT VA SERVERNI BIR VAQTDA ISHGA TUSHIRISH
if __name__ == "__main__":
    # Serverni alohida oqimda (Thread) yurgizamiz
    server_thread = Thread(target=run_server)
    server_thread.start()
    
    # Bot pollingni boshlaymiz
    bot.polling(none_stop=True)

