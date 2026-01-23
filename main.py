import requests
import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup

# 1. Server qismi (Render uchun)
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

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# 2. Ob-havo funksiyasi (Aniqroq algoritm)
def get_weather(city):
    try:
        url = f"https://obhavo.uz/{city}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        current = soup.find("div", class_="current-forecast").find("strong").text.strip()
        desc = soup.find("div", class_="current-forecast").find("span").text.strip()
        
        # Kechasi va kunduzi haroratini olish
        forecast = soup.find("table", class_="weather-table")
        temp_cols = forecast.find_all("span", class_="forecast-temp")
        day_temp = temp_cols[0].text.strip()
        night_temp = temp_cols[1].text.strip()
        
        res = f"📍 **{city.capitalize()} ob-havosi:**\n\n"
        res += f"🌡 Hozir: {current}\n"
        res += f"☀️ Kunduzi: {day_temp}\n"
        res += f"🌙 Kechasi: {night_temp}\n"
        res += f"☁️ Holat: {desc}\n\n"
        res += f"🔗 [Batafsil obhavo.uz saytida]({url})"
        return res
    except:
        return "⚠️ Kechirasiz, ob-havo ma'lumotlarini yuklashda xatolik. Sayt vaqtincha band bo'lishi mumkin."

# 3. Yangiliklar va Sport (Kuchaytirilgan qidiruv)
def get_news(url_type):
    urls = {
        "gen": "https://kun.uz/news/rss",
        "sport": "https://championat.asia/uz/news/rss"
    }
    try:
        r = requests.get(urls[url_type], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.content, 'xml')
        items = soup.find_all('item')
        res = []
        for i in items[:10]:
            title = i.title.text
            link = i.link.text
            icon = "🔴" if url_type == "gen" else "⚽️"
            res.append(f"{icon} {title}\n🔗 [Ochish]({link})")
        return "\n\n".join(res)
    except:
        return "⚠️ Ma'lumot topilmadi. Sayt ulanishni rad etdi."

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\nMarhamat, bo'limni tanlang: 👇", 
                     reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add("📰 So'nggi Yangiliklar", "🏆 Sport/Futbol", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar"))

@bot.message_handler(func=lambda m: True)
def handle(m):
    if m.text == "📰 So'nggi Yangiliklar":
        bot.send_message(m.chat.id, "⏳ Yangiliklar yuklanmoqda...")
        bot.send_message(m.chat.id, get_news("gen"), parse_mode="Markdown", disable_web_page_preview=True)
    elif m.text == "🏆 Sport/Futbol":
        bot.send_message(m.chat.id, "⏳ Sport xabarlari qidirilmoqda...")
        bot.send_message(m.chat.id, get_news("sport"), parse_mode="Markdown", disable_web_page_preview=True)
    elif m.text == "💰 Valyuta":
        r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        res = "💰 **Valyuta kursi (Markaziy Bank):**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
        bot.send_message(m.chat.id, res)
    elif m.text == "🎬 Kinolar":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in [("🔥 Jangovar", "k_1"), ("😂 Komediya", "k_2"), ("😱 Qo'rqinchli", "k_3"), ("🎭 Drama", "k_4"), ("🚀 Fantastika", "k_5"), ("👶 Multfilm", "k_6")]])
        bot.send_message(m.chat.id, "🎥 Janrni tanlang:", reply_markup=kb)
    elif m.text == "🌤 Ob-havo":
        kb = types.InlineKeyboardMarkup(row_width=3)
        cities = [("Toshkent", "tashkent"), ("Samarqand", "samarkand"), ("Andijon", "andijan"), ("Farg'ona", "ferghana"), ("Namangan", "namangan"), ("Buxoro", "bukhara"), ("Xiva", "khiva"), ("Qarshi", "karshi"), ("Termiz", "termez")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=f"w_{d}") for t, d in cities])
        bot.send_message(m.chat.id, "🌤 Viloyatni tanlang:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, get_weather(call.data[2:]), parse_mode="Markdown")
    elif call.data.startswith("k_"):
        kinolar = {
            "k_1": "🔥 **Jangovar (TOP 10):**\n1. [Jon Uik 4](https://uzbekcha.net/search?q=Jon+Uik)\n2. [Forsaj 10](https://uzbekcha.net/search?q=Forsaj)\n3. [Batman](https://uzbekcha.net/search?q=Batman)\n4. [Gladiator](https://uzbekcha.net/search?q=Gladiator)\n5. [Ekvalayzer](https://uzbekcha.net/search?q=Ekvalayzer)\n6. [Top Gan](https://uzbekcha.net/search?q=Top+Gan)\n7. [Kingsman](https://uzbekcha.net/search?q=Kingsman)\n8. [Rembo](https://uzbekcha.net/search?q=Rembo)\n9. [Shiddatli](https://uzbekcha.net/search?q=Shiddatli)\n10. [Missiya: Imkonsiz](https://uzbekcha.net/search?q=Missiya)",
            "k_2": "😂 **Komediya (TOP 10):**\n1. [1+1](https://uzbekcha.net/search?q=1+1)\n2. [Maska](https://uzbekcha.net/search?q=Maska)\n3. [Taksichi](https://uzbekcha.net/search?q=Taksichi)\n4. [Uyda yolg'iz](https://uzbekcha.net/search?q=Uyda)\n5. [Jan Ingliz](https://uzbekcha.net/search?q=Jan+Ingliz)\n6. [Katta bolalar](https://uzbekcha.net/search?q=Bolalar)\n7. [Diktator](https://uzbekcha.net/search?q=Diktator)\n8. [O'shanda](https://uzbekcha.net/search?q=O%27shanda)\n9. [Yomon yigitlar](https://uzbekcha.net/search?q=Yigitlar)\n10. [Sardorlar](https://uzbekcha.net/search?q=Sardorlar)",
            "k_3": "😱 **Qo'rqinchli (TOP 10):**\n1. [Astral](https://uzbekcha.net/search?q=Astral)\n2. [It](https://uzbekcha.net/search?q=It)\n3. [Arra](https://uzbekcha.net/search?q=Arra)\n4. [Tavba](https://uzbekcha.net/search?q=Tavba)\n5. [Qo'ng'iroq](https://uzbekcha.net/search?q=Qongiroq)\n6. [Oyna](https://uzbekcha.net/search?q=Oyna)\n7. [O'rmon](https://uzbekcha.net/search?q=Ormon)\n8. [Labirint](https://uzbekcha.net/search?q=Labirint)\n9. [Mumiya](https://uzbekcha.net/search?q=Mumiya)\n10. [Zombi](https://uzbekcha.net/search?q=Zombi)",
            "k_4": "🎭 **Drama (TOP 10):**\n1. [Titanik](https://uzbekcha.net/search?q=Titanik)\n2. [Xatiko](https://uzbekcha.net/search?q=Xatiko)\n3. [7-palata](https://uzbekcha.net/search?q=7-palata)\n4. [Joker](https://uzbekcha.net/search?q=Joker)\n5. [Yashil yo'lak](https://uzbekcha.net/search?q=Yo%27lak)\n6. [Lion](https://uzbekcha.net/search?q=Lion)\n7. [Pianinochi](https://uzbekcha.net/search?q=Pianinochi)\n8. [Shoushenk](https://uzbekcha.net/search?q=Shoushenk)\n9. [Hayot go'zal](https://uzbekcha.net/search?q=Hayot)\n10. [Mahallada duv-duv gap](https://uzbekcha.net/search?q=Mahallada)",
            "k_5": "🚀 **Fantastika (TOP 10):**\n1. [Avatar](https://uzbekcha.net/search?q=Avatar)\n2. [Interstellar](https://uzbekcha.net/search?q=Interstellar)\n3. [Dyuna](https://uzbekcha.net/search?q=Dyuna)\n4. [Matritsa](https://uzbekcha.net/search?q=Matritsa)\n5. [Marslik](https://uzbekcha.net/search?q=Marslik)\n6. [Marvel](https://uzbekcha.net/search?q=Marvel)\n7. [Star Wars](https://uzbekcha.net/search?q=Wars)\n8. [Tenet](https://uzbekcha.net/search?q=Tenet)\n9. [Boshlanish](https://uzbekcha.net/search?q=Boshlanish)\n10. [Transformerlar](https://uzbekcha.net/search?q=Transformerlar)",
            "k_6": "👶 **Multfilmlar (TOP 10):**\n1. [Shrek](https://uzbekcha.net/search?q=Shrek)\n2. [Panda](https://uzbekcha.net/search?q=Panda)\n3. [Koko](https://uzbekcha.net/search?q=Koko)\n4. [Muzlik davri](https://uzbekcha.net/search?q=Muzlik)\n5. [Madagaskar](https://uzbekcha.net/search?q=Madagaskar)\n6. [Moana](https://uzbekcha.net/search?q=Moana)\n7. [Ratatuy](https://uzbekcha.net/search?q=Ratatuy)\n8. [Qahramonlar](https://uzbekcha.net/search?q=Qahramonlar)\n9. [Zootopiya](https://uzbekcha.net/search?q=Zootopiya)\n10. [Nemo](https://uzbekcha.net/search?q=Nemo)"
        }
        bot.send_message(call.message.chat.id, kinolar.get(call.data, "Tez kunda..."), parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

bot.polling(none_stop=True)

