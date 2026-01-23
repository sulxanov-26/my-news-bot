import requests, telebot, os
from telebot import types
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# 1. RENDER UCHUN PORT (MAJBURIY)
app = Flask('')
@app.route('/')
def home(): return "Bot Live!"

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8468486478:AAEQOVdLYDAf42lthIgBibw1Whz-YiR8XYc"
bot = telebot.TeleBot(TOKEN)

# 2. OB-HAVO (AVVALGI SAYTDAN O'QIYDIGAN USUL)
def get_weather_old(city_name):
    try:
        # Shahar nomini kichik harfga o'tkazamiz
        city = city_name.lower().replace("'", "").replace("`", "")
        url = f"https://obhavo.uz/{city}"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml') # lxml bu yerda shart
        
        # Saytdan ma'lumotlarni qidirish
        temp = soup.find('div', class_='current-forecast-desc').find('strong').text
        day_temp = soup.find('div', class_='current-forecast-day').text.strip()
        night_temp = soup.find('div', class_='current-forecast-night').text.strip()
        
        return f"🌤 **{city_name} viloyati:**\n\n🌡 Hozir: {temp}\n☀️ Kun: {day_temp}\n🌙 Tun: {night_temp}"
    except:
        return "⚠️ Bu viloyat bo'yicha ma'lumot topilmadi yoki sayt band."

# 3. KINOLAR BAZASI
movies_data = {
    "k_1": [("Jon Uik 4", "https://uzmovi.com/search?q=John+Wick"), ("Forsaj 10", "https://uzmovi.com/search?q=Fast")],
    "k_2": [("1+1", "https://uzmovi.com/search?q=Intouchables"), ("Maska", "https://uzmovi.com/search?q=Mask")],
    "k_3": [("Astral", "https://uzmovi.com/search?q=Insidious"), ("Anabell", "https://uzmovi.com/search?q=Annabelle")],
    "k_4": [("Avatar", "https://uzmovi.com/search?q=Avatar"), ("Tor", "https://uzmovi.com/search?q=Thor")],
    "k_5": [("Titanik", "https://uzmovi.com/search?q=Titanic"), ("Joker", "https://uzmovi.com/search?q=Joker")],
    "k_6": [("Shrek", "https://uzmovi.com/search?q=Shrek"), ("Moana", "https://uzmovi.com/search?q=Moana")]
}

@bot.message_handler(commands=['start'])
def start(m):
    # Foydalanuvchi ismini olish
    name = m.from_user.first_name
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📰 So'nggi Yangiliklar", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    bot.send_message(m.chat.id, f"Assalomu Alaykum **{name}**!\n\nMarhamat, kerakli bo'limni tanlang:", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_text(m):
    if m.text == "📰 So'nggi Yangiliklar":
        try:
            r = requests.get("https://kun.uz/news/rss")
            soup = BeautifulSoup(r.content, 'xml')
            items = soup.find_all('item')[:10]
            res = "".join([f"🔴 {i.title.text}\n🔗 [Ochish]({i.link.text})\n\n" for i in items])
            bot.send_message(m.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
        except: bot.send_message(m.chat.id, "⚠️ Yangiliklar yuklanmadi.")

    elif m.text == "💰 Valyuta":
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            res = "💰 **Valyuta kursi (MB):**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
            bot.send_message(m.chat.id, res)
        except: bot.send_message(m.chat.id, "⚠️ Valyuta sayti band.")

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
def calls(call):
    if call.data.startswith("w_"):
        city = call.data[2:]
        bot.send_message(call.message.chat.id, get_weather_old(city), parse_mode="Markdown")
    elif call.data.startswith("k_"):
        res = "🎬 **Kinolar:**\n\n" + "\n".join([f"🔹 [{n}]({l})" for n, l in movies_data[call.data]])
        bot.send_message(call.message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
