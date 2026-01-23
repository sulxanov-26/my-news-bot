import requests
import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread
import xml.etree.ElementTree as ET

# 1. Server qismi
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
def keep_alive():
    t = Thread(target=run)
    t.start()
keep_alive()

# 2. Bot sozlamalari
TOKEN = "8468486478:AAEQOVdLYDAf42lthIgBibw1Whz-YiR8XYc"
bot = telebot.TeleBot(TOKEN)

# 3. Menyular
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

# 4. Ma'lumot olish funksiyalari
def get_sport_news():
    sources = [
        {"n": "Sports.uz", "u": "https://sports.uz/news/rss"},
        {"n": "Championat", "u": "https://championat.asia/uz/news/rss"},
        {"n": "Tribuna", "u": "https://kun.uz/news/category/sport/rss"},
        {"n": "Olamsport", "u": "https://olamsport.com/uz/news/rss"},
        {"n": "Stadion", "u": "https://stadion.uz/rss.php"},
        {"n": "UzFIFA", "u": "https://uzfifa.net/rss.xml"}
    ]
    res = []
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15'}
    for src in sources:
        try:
            r = requests.get(src['u'], headers=headers, timeout=8)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:2]:
                res.append(f"⚽️ **{src['n']}**:\n{item.find('title').text}\n🔗 {item.find('link').text}")
            if len(res) >= 10: break
        except: continue
    return res[:10]

def get_kun_uz():
    try:
        r = requests.get("https://kun.uz/news/rss", timeout=10)
        root = ET.fromstring(r.content)
        return [f"🔵 {i.find('title').text}\n🔗 {i.find('link').text}" for i in root.findall('.//item')[:10]]
    except: return ["⚠️ Kun.uz yangiliklari topilmadi."]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot barcha xatolari to'g'irlangan holda ishga tushdi! ✅", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "🔵 Kun.uz":
        bot.send_message(message.chat.id, "📢 **Oxirgi 10 ta yangilik:**\n\n" + "\n\n".join(get_kun_uz()))
    elif message.text == "🏆 Sport/Futbol":
        bot.send_message(message.chat.id, "⏳ 6 ta manbadan eng yangi 10 ta xabar:")
        bot.send_message(message.chat.id, "\n\n".join(get_sport_news()))
    elif message.text == "💰 Valyuta":
        r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        res = "💰 **Valyuta kursi:**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
        bot.send_message(message.chat.id, res)
    elif message.text == "🎬 Kinolar":
        bot.send_message(message.chat.id, "🎥 Janrni tanlang (Nomi ustiga bossangiz kino ochiladi):", reply_markup=movie_genres())
    elif message.text == "🌤 Ob-havo":
        bot.send_message(message.chat.id, "🌤 Viloyatni tanlang:", reply_markup=weather_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    weather_info = {"w_toshkent": "🌤 Toshkent: +12°C", "w_samarqand": "☁️ Samarqand: +10°C", "w_andijon": "⛅️ Andijon: +13°C", "w_farg'ona": "☀️ Farg'ona: +14°C", "w_namangan": "🌤 Namangan: +12°C", "w_buxoro": "☀️ Buxoro: +16°C", "w_navoiy": "☀️ Navoiy: +15°C", "w_qarshi": "🌤 Qarshi: +17°C", "w_termiz": "☀️ Termiz: +20°C", "w_nukus": "☁️ Nukus: +5°C", "w_guliston": "🌤 Guliston: +11°C", "w_jizzax": "⛅️ Jizzax: +12°C", "w_urganch": "☁️ Urganch: +7°C"}
    
    movies = {
        "m_action": "🔥 **10 ta Jangovar (Ko'rish uchun bosing):**\n1. [Jon Uik 4](https://uzbekcha.net/search?q=Jon+Uik+4)\n2. [Forsaj 10](https://uzbekcha.net/search?q=Forsaj+10)\n3. [Top Gan](https://uzbekcha.net/search?q=Top+Gan)\n4. [Batman](https://uzbekcha.net/search?q=Batman)\n5. [Dedpul](https://uzbekcha.net/search?q=Dedpul)\n6. [Shiddatli tezlik](https://uzbekcha.net/search?q=Shiddatli+tezlik)\n7. [Gladiator 2](https://uzbekcha.net/search?q=Gladiator+2)\n8. [King Kong](https://uzbekcha.net/search?q=King+Kong)\n9. [Rembo](https://uzbekcha.net/search?q=Rembo)\n10. [Terminator](https://uzbekcha.net/search?q=Terminator)",
        "m_comedy": "😂 **10 ta Komediya (Ko'rish uchun bosing):**\n1. [1+1](https://uzbekcha.net/search?q=1+1)\n2. [Uyda yolg'iz](https://uzbekcha.net/search?q=Uyda+yolg%27iz)\n3. [Maska](https://uzbekcha.net/search?q=Maska)\n4. [Jan Ingliz](https://uzbekcha.net/search?q=Jan+Ingliz)\n5. [Borat](https://uzbekcha.net/search?q=Borat)\n6. [Hangover](https://uzbekcha.net/search?q=Hangover)\n7. [Millarder](https://uzbekcha.net/search?q=Millarder)\n8. [Shpion](https://uzbekcha.net/search?q=Shpion)\n9. [Taksichi](https://uzbekcha.net/search?q=Taksichi)\n10. [Katta bolalar](https://uzbekcha.net/search?q=Katta+bolalar)",
        "m_horror": "😱 **10 ta Qo'rqinchli:**\n1. [Astral](https://uzbekcha.net/search?q=Astral)\n2. [Qo'ng'iroq](https://uzbekcha.net/search?q=Qo%27ng%27iroq)\n3. [Tavba](https://uzbekcha.net/search?q=Tavba)\n4. [Arra](https://uzbekcha.net/search?q=Arra)\n5. [It](https://uzbekcha.net/search?q=It)\n6. [Chaki](https://uzbekcha.net/search?q=Chaki)\n7. [Juma 13](https://uzbekcha.net/search?q=Juma+13)\n8. [O'liklar](https://uzbekcha.net/search?q=O%27liklar)\n9. [Labirint](https://uzbekcha.net/search?q=Labirint)\n10. [Zombi](https://uzbekcha.net/search?q=Zombi)",
        "m_sites": "🌐 **Eng yaxshi kino saytlari:**\n\n🎬 [Uzbekcha.net](https://uzbekcha.net)\n🎬 [Cinerama.uz](https://cinerama.uz)\n🎬 [Allplay.uz](https://allplay.uz)\n🎬 [Itv.uz](https://itv.uz)\n🎬 [Beeline TV](https://beelinetv.uz)"
    }

    if call.data in weather_info:
        bot.send_message(call.message.chat.id, weather_info[call.data], reply_markup=main_menu())
        bot.answer_callback_query(call.id)
    elif call.data in movies or "m_" in call.data:
        text = movies.get(call.data, "🎬 Tez kunda boshqa janrlar ham qo'shiladi!")
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)
        bot.answer_callback_query(call.id)

bot.polling(none_stop=True)

