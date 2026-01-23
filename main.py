import requests
import telebot
from telebot import types
from bs4 import BeautifulSoup

TOKEN = "8468486478:AAEQOVdLYDAf42lthIgBibw1Whz-YiR8XYc"
bot = telebot.TeleBot(TOKEN)

# 🌤 OB-HAVO (Bloklanmaydigan API usuli)
def get_weather(city):
    try:
        # Bu API kaliti ochiq va bepul ishlaydi
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=b713020054700d98192801e0e8e97495&units=metric&lang=uz"
        data = requests.get(url, timeout=10).json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        return f"📍 **{city.upper()}**\n\n🌡 Harorat: {temp}°C\n☁️ Holat: {desc.capitalize()}"
    except:
        return "⚠️ Ob-havo ma'lumotini hozircha olib bo'lmadi."

# 🎬 KINOLAR BAZASI
movies = {
    "k_1": [("Jon Uik 4", "https://uzmovi.com/search?q=John+Wick"), ("Forsaj 10", "https://uzmovi.com/search?q=Fast"), ("Gladiator", "https://uzmovi.com/search?q=Gladiator"), ("Betmen", "https://uzmovi.com/search?q=Batman"), ("Top Gan", "https://uzmovi.com/search?q=Top+Gun"), ("T-34", "https://uzmovi.com/search?q=T-34"), ("Ekvalayzer", "https://uzmovi.com/search?q=Equalizer"), ("Kingsman", "https://uzmovi.com/search?q=Kingsman"), ("Missiya bajarilmas", "https://uzmovi.com/search?q=Mission"), ("Rembo", "https://uzmovi.com/search?q=Rambo")],
    "k_2": [("1+1", "https://uzmovi.com/search?q=Intouchables"), ("Maska", "https://uzmovi.com/search?q=Mask"), ("Taksichi", "https://uzmovi.com/search?q=Taxi"), ("Uyda yolg'iz", "https://uzmovi.com/search?q=Home"), ("Katta bolalar", "https://uzmovi.com/search?q=Grown"), ("Diktator", "https://uzmovi.com/search?q=Dictator"), ("Jan Ingliz", "https://uzmovi.com/search?q=Johnny"), ("Yomon yigitlar", "https://uzmovi.com/search?q=Bad"), ("Sardorlar", "https://uzmovi.com/search?q=Captains"), ("Kruella", "https://uzmovi.com/search?q=Cruella")],
    "k_3": [("Anabell", "https://uzmovi.com/search?q=Annabelle"), ("Astral", "https://uzmovi.com/search?q=Insidious"), ("O'liklar", "https://uzmovi.com/search?q=Dead"), ("Arvoh", "https://uzmovi.com/search?q=Ghost"), ("Nafas olma", "https://uzmovi.com/search?q=Breathe"), ("O'yin", "https://uzmovi.com/search?q=Game"), ("Tuzoq", "https://uzmovi.com/search?q=Trap"), ("Qichqiriq", "https://uzmovi.com/search?q=Scream"), ("Arra", "https://uzmovi.com/search?q=Saw"), ("Zulmat", "https://uzmovi.com/search?q=Dark")],
    "k_4": [("Avatar", "https://uzmovi.com/search?q=Avatar"), ("O'rgimchak odam", "https://uzmovi.com/search?q=Spider"), ("Tor", "https://uzmovi.com/search?q=Thor"), ("Iron Man", "https://uzmovi.com/search?q=Iron"), ("Interstellar", "https://uzmovi.com/search?q=Interstellar"), ("Marslik", "https://uzmovi.com/search?q=Martian"), ("Duna", "https://uzmovi.com/search?q=Dune"), ("Yulduzlar jangi", "https://uzmovi.com/search?q=Wars"), ("Godzilla", "https://uzmovi.com/search?q=Godzilla"), ("Transformatorlar", "https://uzmovi.com/search?q=Transformers")],
    "k_5": [("Yashil yo'lak", "https://uzmovi.com/search?q=Green"), ("Titanik", "https://uzmovi.com/search?q=Titanic"), ("Hachiko", "https://uzmovi.com/search?q=Hachiko"), ("Legend", "https://uzmovi.com/search?q=Legend"), ("Skarfeys", "https://uzmovi.com/search?q=Scarface"), ("Joker", "https://uzmovi.com/search?q=Joker"), ("Parazit", "https://uzmovi.com/search?q=Parasite"), ("Sherlok", "https://uzmovi.com/search?q=Sherlock"), ("Pianinochi", "https://uzmovi.com/search?q=Pianist"), ("Leon", "https://uzmovi.com/search?q=Leon")],
    "k_6": [("Qirol Sher", "https://uzmovi.com/search?q=Lion"), ("Shrek", "https://uzmovi.com/search?q=Shrek"), ("Kung-fu Panda", "https://uzmovi.com/search?q=Panda"), ("Muzlik davri", "https://uzmovi.com/search?q=Ice"), ("Moana", "https://uzmovi.com/search?q=Moana"), ("Koko", "https://uzmovi.com/search?q=Coco"), ("Ratauy", "https://uzmovi.com/search?q=Ratatouille"), ("Luka", "https://uzmovi.com/search?q=Luca"), ("Minionlar", "https://uzmovi.com/search?q=Minions"), ("Madagaskar", "https://uzmovi.com/search?q=Madagascar")]
}

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📰 So'nggi Yangiliklar", "💰 Valyuta", "🌤 Ob-havo", "🎬 Kinolar")
    bot.send_message(m.chat.id, "Assalomu Alaykum Profil egasi 👋", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def main_menu(m):
    if m.text == "📰 So'nggi Yangiliklar":
        try:
            r = requests.get("https://kun.uz/news/rss", timeout=10)
            soup = BeautifulSoup(r.content, 'xml')
            items = soup.find_all('item')[:10]
            res = ""
            for i in items:
                res += f"🔴 {i.title.text}\n🔗 [Ochish]({i.link.text})\n\n"
            bot.send_message(m.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
        except:
            bot.send_message(m.chat.id, "⚠️ Yangiliklarni yuklashda muammo.")

    elif m.text == "💰 Valyuta":
        try:
            r = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            res = "💰 **Valyuta kurslari (MB):**\n\n" + "\n".join([f"🔹 1 {i['Ccy']} = {i['Rate']} so'm" for i in r[:10]])
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
        janrlar = [("🔥 Jangovar", "k_1"), ("😂 Komediya", "k_2"), ("😱 Qo'rqinchli", "k_3"), ("🚀 Fantastika", "k_4"), ("🎭 Drama", "k_5"), ("👶 Multfilm", "k_6")]
        kb.add(*[types.InlineKeyboardButton(t, callback_data=d) for t, d in janrlar])
        bot.send_message(m.chat.id, "🎥 Janrni tanlang:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data.startswith("w_"):
        bot.send_message(call.message.chat.id, get_weather(call.data[2:]), parse_mode="Markdown")
    elif call.data.startswith("k_"):
        res = "🎬 **Siz tanlagan janr bo'yicha TOP 10 film:**\n\n"
        for idx, (name, link) in enumerate(movies[call.data], 1):
            res += f"{idx}. [{name}]({link})\n"
        bot.send_message(call.message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

bot.polling(none_stop=True)


