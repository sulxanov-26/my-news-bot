import requests, telebot, os, time
from telebot import types
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup

# 1. RENDER SERVERI (24/7 ISHLASH UCHUN)
app = Flask('')
@app.route('/')
def home(): return "Bot Live! ✅"

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# DIQQAT: TOKENNI BOTFATHERDAN YANGILAB QO'YING!
TOKEN = "8468486478:AAEQOVdLYDAf42lthIgBibw1Whz-YiR8XYc"
bot = telebot.TeleBot(TOKEN)

# 2. KESH TIZIMI (API bosimini kamaytirish va tezlik uchun)
weather_cache = {}
currency_cache = {"data": None, "time": 0}

# OB-HAVO FUNKSIYASI (KESH BILAN)
def get_weather(city_en):
    now = time.time()
    # Agar keshda bo'lsa va 15 daqiqa o'tmagan bo'lsa keshdan oladi
    if city_en in weather_cache and (now - weather_cache[city_en]['time']) < 900:
        return weather_cache[city_en]['text']
    
    try:
        url = f"https://wttr.in/{city_en}?format=%c+%t"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            uz_names = {
                "Tashkent":"Toshkent", "Samarkand":"Samarqand", "Andijan":"Andijon",
                "Fergana":"Farg'ona", "Namangan":"Namangan", "Bukhara":"Buxoro",
                "Navoi":"Navoiy", "Karshi":"Qarshi", "Termez":"Termiz",
                "Nukus":"Nukus", "Guliston":"Guliston", "Jizzakh":"Jizzax", "Urgench":"Urganch"
            }
            res_text = f"🌤 {uz_names.get(city_en, city_en)}: {r.text.strip()}"
            weather_cache[city_en] = {'text': res_text, 'time': now}
            return res_text
        return "⚠️ Ma'lumot topilmadi."
    except:
        return "⚠️ Ob-havo xizmati band."

# 3. KINOLAR BAZASI (60 TA FILM)
movies_data = {
    "k_1": [("Jon Uik 4", "https://uzmovi.com/filmlar/john-wick-4"), ("Forsaj 10", "https://uzmovi.com/filmlar/fast-x"), ("Dedpul", "https://uzmovi.com/filmlar/deadpool"), ("Gladiator", "https://uzmovi.com/filmlar/gladiator"), ("Top Gan", "https://uzmovi.com/filmlar/top-gun"), ("Betmen", "https://uzmovi.com/filmlar/the-batman"), ("Spiderman", "https://uzmovi.com/filmlar/spider-man"), ("Kingsman", "https://uzmovi.com/filmlar/kingsman"), ("Reaktiv", "https://uzmovi.com/filmlar/extraction"), ("Transfomer", "https://uzmovi.com/filmlar/transformers")],
    "k_2": [("1+1", "https://uzmovi.com/filmlar/the-intouchables"), ("Maska", "https://uzmovi.com/filmlar/the-mask"), ("Uyda yolg'iz", "https://uzmovi.com/filmlar/home-alone"), ("Janob Bin", "https://uzmovi.com/filmlar/mr-bean"), ("Diktator", "https://uzmovi.com/filmlar/the-dictator"), ("Ted", "https://uzmovi.com/filmlar/ted"), ("Oshpaz", "https://uzmovi.com/filmlar/chef"), ("Free Guy", "https://uzmovi.com/filmlar/free-guy"), ("Katta yigit", "https://uzmovi.com/filmlar/big"), ("Oshpaz-2", "https://uzmovi.com/filmlar/chef-2")],
    "k_3": [("Astral", "https://uzmovi.com/filmlar/insidious"), ("Anabell", "https://uzmovi.com/filmlar/annabelle"), ("Chaqiriq", "https://uzmovi.com/filmlar/the-conjuring"), ("Nunn", "https://uzmovi.com/filmlar/the-nun"), ("Arr", "https://uzmovi.com/filmlar/saw"), ("IT", "https://uzmovi.com/filmlar/it"), ("Zulmat", "https://uzmovi.com/filmlar/lights-out"), ("Tungi ov", "https://uzmovi.com/filmlar/night-hunt"), ("Qabriston", "https://uzmovi.com/filmlar/cemetery"), ("Vahima", "https://uzmovi.com/filmlar/panic")],
    "k_4": [("Avatar", "https://uzmovi.com/filmlar/avatar"), ("Tor", "https://uzmovi.com/filmlar/thor"), ("Marslik", "https://uzmovi.com/filmlar/the-martian"), ("Interstellar", "https://uzmovi.com/filmlar/interstellar"), ("Tenet", "https://uzmovi.com/filmlar/tenet"), ("Duna", "https://uzmovi.com/filmlar/dune"), ("Inception", "https://uzmovi.com/filmlar/inception"), ("Matrix", "https://uzmovi.com/filmlar/the-matrix"), ("Prometey", "https://uzmovi.com/filmlar/prometheus"), ("Star Wars", "https://uzmovi.com/filmlar/star-wars")],
    "k_5": [("Titanik", "https://uzmovi.com/filmlar/titanic"), ("Joker", "https://uzmovi.com/filmlar/joker"), ("Yashil mil", "https://uzmovi.com/filmlar/the-green-mile"), ("Sherlok", "https://uzmovi.com/filmlar/sherlock"), ("Otam", "https://uzmovi.com/filmlar/the-father"), ("Lala Land", "https://uzmovi.com/filmlar/la-la-land"), ("Parazit", "https://uzmovi.com/filmlar/parasite"), ("Leon", "https://uzmovi.com/filmlar/leon"), ("Skarfeys", "https://uzmovi.com/filmlar/scarface"), ("Yetti", "https://uzmovi.com/filmlar/seven")],
    "k_6": [("Shrek", "https://uzmovi.com/filmlar/shrek"), ("Moana", "https://uzmovi.com/filmlar/moana"), ("Kung-fu Panda", "https://uzmovi.com/filmlar/kung-fu-panda"), ("Rio", "https://uzmovi.com/filmlar/rio"), ("Muzlik davri", "https://uzmovi.com/filmlar/ice-age"), ("Madagaskar", "https://uzmovi.com/filmlar/madagascar"), ("Koko", "https://uzmovi.com/filmlar/coco"), ("Luka", "https://uzmovi.com/filmlar/luca"), ("Raya", "https://uzmovi.com/filmlar/raya"), ("Zootopiya", "https://uzmovi.com/filmlar/zootopia")]
}

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # TUGMALAR NOMINI YANGILADIK (KATTA HARFLARDA)
    kb.add("📰 KUN.UZ YANGILIKLAR", "💰 VALYUTA", "🌤 OB-HAVO", "🎬 KINOLAR")
    bot.send_message(m.chat.id, f"Assalomu Alaykum! Bo'limni tanlang:", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def main_menu(m):
    txt = m.text.upper()
    
    if "KUN.UZ" in txt:
        try:
            r = requests.get("https://kun.uz/news/rss")
            soup = BeautifulSoup(r.content, 'xml')
            res = "".join([f"🔴 {i.title.text}\n🔗 [Ochish]({i.link.text})\n\n" for i in soup.find_all('item')[:10]])
            bot.send_message(m.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
        except: bot.send_message(m.chat.id, "⚠️ Yangiliklar yuklanmadi.")

    elif "VALYUTA" in txt:
        now = time.time()
        # Valyuta keshini tekshirish (1 soatda bir yangilanadi)
        if not currency_cache["data"] or (now - currency_cache["time"]) > 3600:
            try:
                r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
                currency_cache["data"] = r[:10]
                currency_cache["time"] = now
            except: pass
        
        if currency_cache["data"]:
            res = "💰 **VALYUTA KURSLARI (MB):**\n\n"
            for i in currency_cache["data"]:
                res += f"🔹 1 {i['Ccy']} = {i['Rate']} so'm\n"
            bot.send_message(m.chat.id, res)
        else:
            bot.send_message(m.chat.id, "⚠️ Ma'lumotni olib bo'lmadi.")

    elif "OB-HAVO" in txt:
        kb = types.InlineKeyboardMarkup(row_width=3)
        btns = [("Toshkent", "w_Tashkent"), ("Samarqand", "w_Samarkand"), ("Andijon", "w_Andijan"), ("Farg'ona", "w_Fergana"), ("Namangan", "w_Namangan"), ("Buxoro", "w_Bukhara"), ("Navoiy", "w_Navoi"), ("Qarshi", "w_Karshi"), ("Termiz", "w_Termez"), ("Nukus", "w_Nukus"), ("Guliston", "w_Guliston"), ("Jizzax", "w_Jizzakh"), ("Urgench", "w_Urgench")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in btns])
        bot.send_message(m.chat.id, "🌤 Viloyatni tanlang:", reply_markup=kb)

    elif "KINOLAR" in txt:
        kb = types.InlineKeyboardMarkup(row_width=2)
        j = [("🔥 Jangovar", "k_1"), ("😂 Komediya", "k_2"), ("😱 Qo'rqinchli", "k_3"), ("🚀 Fantastika", "k_4"), ("🎭 Drama", "k_5"), ("👶 Multfilm", "k_6")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in j])
        bot.send_message(m.chat.id, "🎥 Janrni tanlang:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, get_weather(call.data[2:]))
    elif call.data.startswith("k_"):
        res = "🎬 **Kinolar:**\n\n" + "\n".join([f"🔹 [{n}]({l})" for n, l in movies_data[call.data]])
        bot.send_message(call.message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()

