import threading
from flask import Flask
import telebot

# Niche inverted commas ke andar apna Token paste karein
BOT_TOKEN = "8813016822:AAFuSYJCWV9Tw0e0J_29vGhf63oqujOU7OQ"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Namaste! Mera Bot 24/7 chalu ho gaya hai! 🎉")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, f"Aapne likha: {message.text}")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    bot.infinity_polling()
