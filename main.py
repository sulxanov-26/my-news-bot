import requests, telebot, os
from telebot import types
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup

# 1. SERVER SOZLAMASI
app = Flask('')
@app.route('/')
def home(): return "Bot Live! ✅"

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# TOKENNI BOTFATHERDAN YANGILAB QO'YING (Logda 401 xatosi chiqmasligi uchun)
TOKEN = "8468486478:AAGKuA5lJ-VFXOKld5KKNoz4bRFmjeueYOM"
bot = telebot.TeleBot(TOKEN)

# 2. OB-HAVO (INGLIZCHA SO'ROV -> O'ZBEKCHA JAVOB)
def get_weather(city_en):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en}&appid=b713020054700d98192801e0e8e97495&units=metric"
        r = requests.get(url, timeout=10).json()
        temp = int(r['main']['temp'])
        
        # Inglizcha nomlarni o'zbekchaga o'girish lug'ati
        uz_names = {
            "Tashkent": "Toshkent", "Samarkand": "Samarqand", "Andijan": "Andijon",
            "Fergana": "Farg'ona", "Namangan": "Namangan", "Bukhara": "Buxoro",
            "Navoi": "Navoiy", "Karshi": "Qarshi", "Termez": "Termiz",
            "Nukus": "Nukus", "Guliston": "Guliston", "Jizzakh": "Jizzax", "Urgench": "Urganch"
        }
        name = uz_names.get(city_en, city_en)
        return f"🌤 {name}: {temp}°C"
    except:
        return "⚠️ Ob-havo ma'lumotini olishda xatolik."

# 3. KINOLAR BAZASI (NAMUNA)
movies_data = {
    "k_1": [("Jon Uik 4", "https://uzmovi.com/filmlar/john-wick-4"), ("Forsaj 10", "https://uzmovi.com/filmlar/fast-x")],
    "k_2": [("1+1", "https://uzmovi.com/filmlar/the-intouchables"), ("Maska", "https://uzmovi.com/filmlar/the-mask")]
}

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📰 Kun.uz Yangiliklar", "💰 10 ta Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    bot.send_message(m.chat.id, f"Assalomu Alaykum! Bo'limni tanlang:", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def main_menu(m):
    if m.text == "📰 Kun.uz Yangiliklar":
        try:
            r = requests.get("https://kun.uz/news/rss")
            soup = BeautifulSoup(r.content, 'xml')
            res = "".join([f"🔴 {i.title.text}\n🔗 [Ochish]({i.link.text})\n\n" for i in soup.find_all('item')[:10]])
            bot.send_message(m.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
        except: bot.send_message(m.chat.id, "⚠️ Yangiliklar yuklanmadi.")

    elif m.text == "💰 10 ta Valyuta":
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            res = "💰 **Markaziy Bank kursi (10 ta):**\n\n"
            for i in r[:10]: # 10 ta valyutani chiqarish
                res += f"🔹 1 {i['Ccy']} = {i['Rate']} so'm\n"
            bot.send_message(m.chat.id, res, parse_mode="Markdown")
        except: bot.send_message(m.chat.id, "⚠️ Valyuta kursini olib bo'lmadi.")

    elif m.text == "🌤 Ob-havo":
        kb = types.InlineKeyboardMarkup(row_width=3)
        # Callback data'lar inglizcha (API uchun), lekin tugma matni o'zbekcha
        btns = [
            ("Toshkent", "w_Tashkent"), ("Samarqand", "w_Samarkand"), ("Andijon", "w_Andijan"),
            ("Farg'ona", "w_Fergana"), ("Namangan", "w_Namangan"), ("Buxoro", "w_Bukhara"),
            ("Navoiy", "w_Navoi"), ("Qarshi", "w_Karshi"), ("Termiz", "w_Termez"),
            ("Nukus", "w_Nukus"), ("Guliston", "w_Guliston"), ("Jizzax", "w_Jizzakh"), ("Urganch", "w_Urgench")
        ]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in btns])
        bot.send_message(m.chat.id, "🌤 Viloyatni tanlang:", reply_markup=kb)

    elif m.text == "🎬 Kinolar":
        kb = types.InlineKeyboardMarkup(row_width=2)
        j = [("🔥 Jangovar", "k_1"), ("😂 Komediya", "k_2")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in j])
        bot.send_message(m.chat.id, "🎥 Janrni tanlang:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("w_"):
        city_en = call.data[2:] # "Tashkent", "Samarkand" va h.k.
        bot.send_message(call.message.chat.id, get_weather(city_en))
    elif call.data.startswith("k_"):
        res = "🎬 **Kinolar:**\n\n" + "\n".join([f"🔹 [{n}]({l})" for n, l in movies_data[call.data]])
        bot.send_message(call.message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
