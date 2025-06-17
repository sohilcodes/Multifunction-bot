import telebot, requests, json, os
from telebot import types
from datetime import datetime

BOT_TOKEN = '7927385130:AAEbuy_DLGiIcXnyy5snyrsZvLi0jYBCSTY'
ADMIN_ID = 6411315434  # Replace with your Telegram ID

bot = telebot.TeleBot(BOT_TOKEN)

# Ensure users.json exists
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump([], f)

# Add user
def add_user(uid):
    with open("users.json", "r") as f:
        data = json.load(f)
    if uid not in data:
        data.append(uid)
        with open("users.json", "w") as f:
            json.dump(data, f)

# Start
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    add_user(uid)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔗 URL Shortener", "📷 Screenshot")
    markup.row("🧬 QR Gen/Scan", "🔐 Encrypt")
    markup.row("🌐 Translate", "🎙️ TTS")
    if uid == ADMIN_ID:
        markup.row("👨‍💻 Admin Panel")
    bot.send_message(msg.chat.id, "✨ Welcome to All-in-One Bot! Choose a function:", reply_markup=markup)

# URL Shortener
@bot.message_handler(func=lambda m: m.text == "🔗 URL Shortener")
def url_short(msg):
    bot.send_message(msg.chat.id, "Send the URL to shorten:")
    bot.register_next_step_handler(msg, do_shorten)

def do_shorten(msg):
    url = msg.text
    api = f"https://api.shrtco.de/v2/shorten?url={url}"
    try:
        short = requests.get(api).json()['result']['short_link']
        bot.send_message(msg.chat.id, f"🔗 Shortened URL:\n{short}")
    except:
        bot.send_message(msg.chat.id, "❌ Invalid URL!")

# Screenshot
@bot.message_handler(func=lambda m: m.text == "📷 Screenshot")
def screenshot(msg):
    bot.send_message(msg.chat.id, "Send a full URL (with https://):")
    bot.register_next_step_handler(msg, do_screenshot)

def do_screenshot(msg):
    url = msg.text
    api = f"https://image.thum.io/get/width/1200/crop/900/{url}"
    bot.send_photo(msg.chat.id, api)

# QR Code
@bot.message_handler(func=lambda m: m.text == "🧬 QR Gen/Scan")
def qr_option(msg):
    bot.send_message(msg.chat.id, "Send text to generate QR:")
    bot.register_next_step_handler(msg, do_qr)

def do_qr(msg):
    txt = msg.text
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={txt}"
    bot.send_photo(msg.chat.id, qr_url)

# Encrypt
@bot.message_handler(func=lambda m: m.text == "🔐 Encrypt")
def encrypt(msg):
    bot.send_message(msg.chat.id, "Send text to encrypt:")
    bot.register_next_step_handler(msg, do_encrypt)

def do_encrypt(msg):
    encrypted = ''.join([chr(ord(c)+5) for c in msg.text])
    bot.send_message(msg.chat.id, f"🔒 Encrypted:\n{encrypted}")

# Translate
@bot.message_handler(func=lambda m: m.text == "🌐 Translate")
def translate(msg):
    bot.send_message(msg.chat.id, "Send text to translate to Hindi:")
    bot.register_next_step_handler(msg, do_translate)

def do_translate(msg):
    text = msg.text
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|hi"
    data = requests.get(url).json()
    translated = data["responseData"]["translatedText"]
    bot.send_message(msg.chat.id, f"📘 Hindi:\n{translated}")

# TTS
@bot.message_handler(func=lambda m: m.text == "🎙️ TTS")
def tts(msg):
    bot.send_message(msg.chat.id, "Send English text for voice (mp3):")
    bot.register_next_step_handler(msg, do_tts)

def do_tts(msg):
    txt = msg.text
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={txt}&tl=en&client=tw-ob"
    bot.send_audio(msg.chat.id, url)

# Admin Panel
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Admin Panel" and m.from_user.id == ADMIN_ID)
def admin_panel(msg):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 User Count", callback_data="users"))
    markup.add(types.InlineKeyboardButton("📣 Broadcast", callback_data="broadcast"))
    bot.send_message(msg.chat.id, "Admin Panel:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "users")
def show_users(call):
    with open("users.json") as f:
        count = len(json.load(f))
    bot.send_message(call.message.chat.id, f"👥 Total Users: {count}")

@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def ask_broadcast(call):
    msg = bot.send_message(call.message.chat.id, "Send message to broadcast:")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(msg):
    with open("users.json") as f:
        users = json.load(f)
    for u in users:
        try:
            bot.send_message(u, f"📢 Broadcast:\n{msg.text}")
        except:
            pass
    bot.send_message(msg.chat.id, "✅ Broadcast Sent")

# Run the bot
bot.infinity_polling()
