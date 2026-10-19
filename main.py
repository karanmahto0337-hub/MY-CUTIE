import threading
from flask import Flask
import telebot
from google import genai

# 1. Yahan apna Telegram Bot Token daalein
BOT_TOKEN = "8813016822:AAFuSYJCWV9Tw0e0J_29vGhf63oqujOU7OQ"

# 2. Yahan apni nayi Google AI Key (AIzaSy... wali) daalein
GEMINI_API_KEY = "AQ.Ab8RN6KlLbrTgGzWvGwA4JC-HaDvNyJ_yYL80jXvyJy0P7pC5w"

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Namaste! 🤖 Main ek Super AI Bot hoon.\nMujhse koi bhi sawal puchiye, main ChatGPT aur Google ki tarah jawab dunga!"
    )

@bot.message_handler(func=lambda msg: True)
def ai_reply(message):
    try:
        # User ko "Typing..." dikhane ke liye
        bot.send_chat_action(message.chat.id, 'typing')
        
        # AI Dimaag se jawab mangwana
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        
        # User ko jawab bhejna
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, "Maaf karna, abhi mera dimaag thoda busy hai. Ek minute baad puchiye!")
        print(f"Error: {e}")

# --- 24/7 Server Code ---
app = Flask(__name__)

@app.route('/')
def home():
    return "AI Bot is running 24/7!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    bot.infinity_polling()
