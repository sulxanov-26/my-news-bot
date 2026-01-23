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

# 1. Menyu tizimi
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📰 So'nggi Yangiliklar", "🏆 Sport/Futbol", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    return markup

# 2. Yangiliklarni optimallashtirish (Ko'p manbali)
def get_general_news():
    news_sources = [
        {"n": "Kun.uz", "u": "https://kun.uz/news/rss"},
        {"n": "Daryo", "u": "https://daryo.uz/feed/"},
        {"n": "Qalampir", "u": "https://qalampir.uz/uz/news/rss"}
    ]
    all_news = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    for src in news_sources:
        try:
            r = requests.get(src['u'], headers=headers, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:3]: # Har biridan 3 tadan
                title = item.find('title').text
                link = item.find('link').text
                all_news.append(f"🔴 **{src['n']}**:\n{title}\n🔗 [Ochish]({link})")
        except: continue
    return all_news[:10]

# 3. Sportni optimallashtirish
def get_sport_news():
    sport_sources = [
        {"n": "Sports.uz", "u": "https://sports.uz/news/rss"},
        {"n": "Championat", "u": "https://championat.asia/uz/news/rss"},
        {"n": "Stadion", "u": "https://stadion.uz/rss.php"}
    ]
    res = []
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15'}
    for src in sport_sources:
        try:
            r = requests.get(src['u'], headers=headers, timeout=12)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:4]:
                res.append(f"⚽️ **{src['n']}**:\n{item.find('title').text}\n🔗 [Batafsil]({item.find('link').text})")
        except: continue
    return res[:10]

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    welcome_text = f"Assalomu alaykum, {user_name}! 👋\n\nSizning shaxsiy yordamchi botingizga xush kelibsiz! 🚀\n\nKerakli bo'limni tanlang: 👇"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "📰 So'nggi Yangiliklar":
        bot.send_message(message.chat.id, "⏳ Turli manbalardan yangiliklar yig'ilmoqda...")
        news = get_general_news()
        bot.send_message(message.chat.id, "\n\n".join(news) if news else "⚠️ Yangiliklar topilmadi.", parse_mode="Markdown", disable_web_page_preview=True)
    
    elif message.text == "🏆 Sport/Futbol":
        bot.send_message(message.chat.id, "⏳ Sport xabarlari yuklanmoqda...")
        s_news = get_sport_news()
        bot.send_message(message.chat.id, "\n\n".join(s_news) if s_news else "⚠️ Sport xabarlari topilmadi.", parse_mode="Markdown", disable_web_page_preview=True)

    elif message.text == "💰 Valyuta":
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            res = "💰 **Valyuta kursi (MB):**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
            bot.send_message(message.chat.id, res)
        except: bot.send_message(message.chat.id, "⚠️ Kursni yuklashda xatolik.")

    elif message.text == "🎬 Kinolar":
        markup = types.InlineKeyboardMarkup(row_width=2)
        genres = [("🔥 Jangovar", "m_action"), ("😂 Komediya", "m_comedy"), ("😱 Daxshat", "m_horror"), 
                  ("🎭 Drama", "m_drama"), ("🚀 Fantastika", "m_sci_fi"), ("👶 Multfilm", "m_animation"), ("🌐 Saytlar", "m_sites")]
        btns = [types.InlineKeyboardButton(t, callback_data=d) for t, d in genres]
        markup.add(*btns)
        bot.send_message(message.chat.id, "🎥 Janrni tanlang:", reply_markup=markup)

    elif message.text == "🌤 Ob-havo":
        # Viloyatlar menyusi (Oldingi koddagidek qoladi)
        markup = types.InlineKeyboardMarkup(row_width=2)
        regions = [("Toshkent", "w_toshkent"), ("Samarqand", "w_samarqand"), ("Andijon", "w_andijon"), ("Farg'ona", "w_farg'ona")]
        btns = [types.InlineKeyboardButton(t, callback_data=d) for t, d in regions]
        markup.add(*btns)
        bot.send_message(message.chat.id, "🌤 Viloyatni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data.startswith("m_"):
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
    
    elif call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, f"🌤 {call.data[2:].capitalize()} viloyatida ob-havo o'rtacha +12°C")
    
    bot.answer_callback_query(call.id)

bot.polling(none_stop=True)


