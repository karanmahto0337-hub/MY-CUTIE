import threading
from flask import Flask
import telebot
from google import genai

# 1. Apna Telegram Bot Token (Bina kisi space ke)
BOT_TOKEN = "8813016822:AAFuSYJCWV9Tw0e0J_29vGhf63oqujOU7OQ".strip()

# 2. Apni Google AI Key (AIzaSy... se shuru hone wali, bina kisi space ke)
GEMINI_API_KEY = "AQ.Ab8RN6KlLbrTgGzWvGwA4JC-HaDvNyJ_yYL80jXvyJy0P7pC5w".strip()

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Namaste! 🤖 Main ek Super AI Bot hoon.\nMujhse koi bhi sawal puchiye!"
    )

@bot.message_handler(func=lambda msg: True)
def ai_reply(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        # AI se jawab mangwana
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        
        reply_text = response.text
        
        # Telegram ek baar mein 4000 se zyada akshar nahi bhej sakta, isliye tukdo mein bhejenge
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                bot.reply_to(message, reply_text[i:i+4000])
        else:
            bot.reply_to(message, reply_text)
            
    except Exception as e:
        # Ab yeh aapko exact wajah batayega ki kya galti hui hai
        bot.reply_to(message, f"⚠️ Technical Error:\n{str(e)}")
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
