import requests
import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread
import xml.etree.ElementTree as ET

app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
def keep_alive():
    t = Thread(target=run)
    t.start()
keep_alive()

TOKEN = "8468486478:AAEQOVdLYDAf42lthIgBibw1Whz-YiR8XYc"
bot = telebot.TeleBot(TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🔵 Kun.uz", "🏆 Sport/Futbol", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    return markup

def weather_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    regions = [("Toshkent", "w_toshkent"), ("Samarqand", "w_samarqand"), ("Andijon", "w_andijon"), 
               ("Farg'ona", "w_farg'ona"), ("Namangan", "w_namangan"), ("Buxoro", "w_buxoro"), 
               ("Navoiy", "w_navoiy"), ("Qarshi", "w_qarshi"), ("Termiz", "w_termiz"), 
               ("Nukus", "w_nukus"), ("Guliston", "w_guliston"), ("Jizzax", "w_jizzax"), ("Urganch", "w_urganch")]
    btns = [types.InlineKeyboardButton(t, callback_data=d) for t, d in regions]
    markup.add(*btns)
    return markup

def movie_genres():
    markup = types.InlineKeyboardMarkup(row_width=2)
    genres = [("🔥 Jangovar", "m_action"), ("😂 Komediya", "m_comedy"), ("😱 Qo'rqinchli", "m_horror"), 
              ("🎭 Drama", "m_drama"), ("🚀 Fantastika", "m_sci_fi"), ("👶 Multfilmlar", "m_animation"),
              ("🌐 Onlayn Ko'rish", "m_sites")]
    btns = [types.InlineKeyboardButton(t, callback_data=d) for t, d in genres]
    markup.add(*btns)
    return markup

def get_sport_news():
    sources = [
        {"n": "Sports.uz", "u": "https://sports.uz/news/rss"},
        {"n": "Championat", "u": "https://championat.asia/uz/news/rss"},
        {"n": "Tribuna", "u": "https://kun.uz/news/category/sport/rss"},
        {"n": "Stadion", "u": "https://stadion.uz/rss.php"},
        {"n": "Olamsport", "u": "https://olamsport.com/uz/news/rss"}
    ]
    res = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    for src in sources:
        try:
            r = requests.get(src['u'], headers=headers, timeout=15) # Kutish vaqti oshirildi
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                for item in root.findall('.//item')[:3]:
                    title = item.find('title').text
                    link = item.find('link').text
                    res.append(f"⚽️ **{src['n']}**:\n{title}\n🔗 [Batafsil o'qish]({link})")
            if len(res) >= 10: break
        except: continue
    return res[:10]

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Assalomu alaykum, {user_name}! 👋\n\n"
        "Sizning shaxsiy yordamchi botingizga xush kelibsiz! 🚀\n\n"
        "Kerakli bo'limni tanlang: 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "🔵 Kun.uz":
        try:
            r = requests.get("https://kun.uz/news/rss", timeout=10)
            root = ET.fromstring(r.content)
            news = [f"🔵 {i.find('title').text}\n🔗 [Ochish]({i.find('link').text})" for i in root.findall('.//item')[:10]]
            bot.send_message(message.chat.id, "📢 **Kun.uz: Oxirgi 10 ta yangilik:**\n\n" + "\n\n".join(news), parse_mode="Markdown")
        except: bot.send_message(message.chat.id, "⚠️ Yangiliklarni yuklashda xatolik.")
        
    elif message.text == "🏆 Sport/Futbol":
        bot.send_message(message.chat.id, "⏳ Yangiliklar qidirilmoqda...")
        news = get_sport_news()
        if news:
            bot.send_message(message.chat.id, "🏆 **Sport yangiliklari:**\n\n" + "\n\n".join(news), parse_mode="Markdown", disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, "⚠️ Hozirda sport saytlari javob bermayapti. Birozdan so'ng qayta urining.")

    elif message.text == "💰 Valyuta":
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            res = "💰 **Valyuta kursi:**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
            bot.send_message(message.chat.id, res)
        except: bot.send_message(message.chat.id, "⚠️ Kursni olib bo'lmadi.")

    elif message.text == "🎬 Kinolar":
        bot.send_message(message.chat.id, "🎥 Janrni tanlang:", reply_markup=movie_genres())

    elif message.text == "🌤 Ob-havo":
        bot.send_message(message.chat.id, "🌤 Viloyatni tanlang:", reply_markup=weather_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data.startswith("w_"):
        weather_info = {"w_toshkent": "🌤 Toshkent: +12°C", "w_samarqand": "☁️ Samarqand: +10°C", "w_andijon": "⛅️ Andijon: +13°C", "w_farg'ona": "☀️ Farg'ona: +14°C", "w_namangan": "🌤 Namangan: +12°C", "w_buxoro": "☀️ Buxoro: +16°C", "w_navoiy": "☀️ Navoiy: +15°C", "w_qarshi": "🌤 Qarshi: +17°C", "w_termiz": "☀️ Termiz: +20°C", "w_nukus": "☁️ Nukus: +5°C", "w_guliston": "🌤 Guliston: +11°C", "w_jizzax": "⛅️ Jizzax: +12°C", "w_urganch": "☁️ Urganch: +7°C"}
        bot.send_message(call.message.chat.id, weather_info.get(call.data, "Ma'lumot topilmadi."))
    
    elif call.data.startswith("m_"):
        movies = {
            "m_action": "🔥 **Jangovar:**\n1. [Jon Uik 4](https://uzbekcha.net/search?q=Jon+Uik+4)\n2. [Forsaj 10](https://uzbekcha.net/search?q=Forsaj+10)",
            "m_comedy": "😂 **Komediya:**\n1. [1+1](https://uzbekcha.net/search?q=1+1)\n2. [Uyda yolg'iz](https://uzbekcha.net/search?q=Uyda+yolg%27iz)",
            "m_horror": "😱 **Daxshat:**\n1. [Astral](https://uzbekcha.net/search?q=Astral)\n2. [Qo'ng'iroq](https://uzbekcha.net/search?q=Qo%27ng%27iroq)",
            "m_drama": "🎭 **Drama:**\n1. [Titanik](https://uzbekcha.net/search?q=Titanik)\n2. [Yashil yo'lak](https://uzbekcha.net/search?q=Yashil+yo%27lak)",
            "m_sci_fi": "🚀 **Fantastika:**\n1. [Interstellar](https://uzbekcha.net/search?q=Interstellar)\n2. [Avatar](https://uzbekcha.net/search?q=Avatar)",
            "m_animation": "👶 **Multfilmlar:**\n1. [Shrek](https://uzbekcha.net/search?q=Shrek)\n2. [Muzlik davri](https://uzbekcha.net/search?q=Muzlik+davri)",
            "m_sites": "🌐 **Saytlar:**\n🎬 [Uzbekcha.net](https://uzbekcha.net)\n🎬 [Cinerama.uz](https://cinerama.uz)"
        }
        bot.send_message(call.message.chat.id, movies.get(call.data, "Tez kunda..."), parse_mode="Markdown", disable_web_page_preview=True)
    
    bot.answer_callback_query(call.id)

bot.polling(none_stop=True)



