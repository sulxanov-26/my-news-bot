import requests
import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread
import xml.etree.ElementTree as ET

# 1. Server qismi (Render uchun)
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

# 3. Asosiy Menyular
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🔵 Kun.uz", "🏆 Sport/Futbol", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    return markup

def movie_genres():
    markup = types.InlineKeyboardMarkup(row_width=2)
    genres = [("🔥 Jangovar", "m_action"), ("😂 Komediya", "m_comedy"), ("😱 Qo'rqinchli", "m_horror"), 
              ("🎭 Drama", "m_drama"), ("🚀 Fantastika", "m_sci_fi"), ("👶 Multfilmlar", "m_animation"),
              ("🌐 Kino Saytlar", "m_sites")] # Saytlarga havola
    btns = [types.InlineKeyboardButton(t, callback_data=d) for t, d in genres]
    markup.add(*btns)
    return markup

# 4. Sport funksiyasi (Siz chizgan barcha saytlar qo'shildi)
def get_sport_news():
    sources = [
        {"name": "Sports.uz", "url": "https://sports.uz/news/rss"},
        {"name": "Championat.asia", "url": "https://championat.asia/uz/news/rss"},
        {"name": "Tribuna.uz", "url": "https://kun.uz/news/category/sport/rss"},
        {"name": "Stadion.uz", "url": "https://stadion.uz/rss.php"},
        {"name": "Olamsport", "url": "https://olamsport.com/uz/news/rss"},
        {"name": "UzFIFA", "url": "https://uzfifa.net/rss.xml"}
    ]
    res = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for src in sources:
        try:
            r = requests.get(src['url'], headers=headers, timeout=8)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                for item in root.findall('.//item')[:2]:
                    title = item.find('title').text
                    link = item.find('link').text
                    res.append(f"⚽️ **{src['name']}**:\n{title}\n🔗 {link}")
            if len(res) >= 10: break
        except: continue
    
    return res[:10] if res else ["⚠️ Sport saytlari hozirda band. Keyinroq urinib ko'ring."]

# 5. Kun.uz funksiyasi (10 ta yangilik)
def get_kun_uz():
    try:
        r = requests.get("https://kun.uz/news/rss", timeout=10)
        root = ET.fromstring(r.content)
        return [f"🔵 {i.find('title').text}\n🔗 {i.find('link').text}" for i in root.findall('.//item')[:10]]
    except: return ["⚠️ Kun.uz yangiliklarini olib bo'lmadi."]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot hamma funksiyalari bilan tayyor! Bo'limni tanlang:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "🔵 Kun.uz":
        bot.send_message(message.chat.id, "📢 **Kun.uz: Oxirgi 10 ta yangilik:**\n\n" + "\n\n".join(get_kun_uz()))
    elif message.text == "🏆 Sport/Futbol":
        bot.send_message(message.chat.id, "⌛️ Sport saytlaridan 10 ta eng yangi xabar yuklanmoqda...")
        bot.send_message(message.chat.id, "\n\n".join(get_sport_news()))
    elif message.text == "💰 Valyuta":
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            res = "💰 **Valyuta kurslari:**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
            bot.send_message(message.chat.id, res)
        except: bot.send_message(message.chat.id, "⚠️ Kurslarni olib bo'lmadi.")
    elif message.text == "🎬 Kinolar":
        bot.send_message(message.chat.id, "🎥 Janrni tanlang (60 ta sara kino va saytlar):", reply_markup=movie_genres())
    elif message.text == "🌤 Ob-havo":
        # Viloyatlar ro'yxati (avvalgi koddan)
        bot.send_message(message.chat.id, "Viloyatni tanlang:")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    movies = {
        "m_action": "🔥 **10 ta Jangovar:**\n1. Jon Uik 4\n2. Forsaj 10\n3. Top Gan\n4. Batman\n5. Dedpul\n6. Shiddatli tezlik\n7. Gladiator 2\n8. King Kong\n9. Rembo\n10. Terminator",
        "m_comedy": "😂 **10 ta Komediya:**\n1. 1+1\n2. Uyda yolg'iz\n3. Maska\n4. Jan Ingliz\n5. Borat\n6. Hangover\n7. Millarder\n8. Shpion\n9. Taksichi\n10. Katta bolalar",
        "m_horror": "😱 **10 ta Qo'rqinchli:**\n1. Astral\n2. Qo'ng'iroq\n3. Tavba\n4. Arra\n5. It\n6. Chaki\n7. Juma 13\n8. O'liklar\n9. Labirint\n10. Zombi",
        "m_drama": "🎭 **10 ta Drama:**\n1. Titanik\n2. Yashil yo'lak\n3. Xatiko\n4. 7-palata\n5. Hayot go'zal\n6. Joker\n7. Lion\n8. O'tgan kunlar\n9. Shoushenk\n10. Forrest Gamp",
        "m_sci_fi": "🚀 **10 ta Fantastika:**\n1. Interstellar\n2. Avatar\n3. Inception\n4. Marslik\n5. Matritsa\n6. Dyuna\n7. Galaktika\n8. O'rgimchak odam\n9. Avengers\n10. Yulduzlar jangi",
        "m_animation": "👶 **10 ta Multfilm:**\n1. Shrek\n2. Muzlik davri\n3. Panda\n4. Madagaskar\n5. Arslon qirol\n6. Ratatuy\n7. Nemo\n8. Koko\n9. Minionlar\n10. Epoxa",
        "m_sites": "🌐 **Onlayn kino ko'rish saytlari:**\n\n🎬 [ITV.uz](https://itv.uz)\n🎬 [Allplay.uz](https://allplay.uz)\n🎬 [Cinerama.uz](https://cinerama.uz)\n🎬 [Beeline TV](https://beelinetv.uz)\n🎬 [Uzbekcha.net](https://uzbekcha.net)"
    }
    if call.data in movies:
        bot.send_message(call.message.chat.id, movies[call.data], parse_mode="Markdown" if call.data == "m_sites" else None)
        bot.answer_callback_query(call.id)

bot.polling(none_stop=True)



