import os
from flask import Flask, request
import telebot
from google import genai

# 1. Apna Telegram Bot Token daalein
BOT_TOKEN = "8813016822:AAFuSYJCWV9Tw0e0J_29vGhf63oqujOU7OQ".strip()

# 2. Apni Google AI Key (AIzaSy... wali) daalein
GEMINI_API_KEY = "AQ.Ab8RN6KlLbrTgGzWvGwA4JC-HaDvNyJ_yYL80jXvyJy0P7pC5w".strip()

# 3. Apna Render wala Link (https://...onrender.com) yahan daalein
RENDER_URL = "https://my-cutie.onrender.com/".strip().rstrip('/')

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

# --- Bot ke Replies ---
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Namaste! 🤖 Main Super AI Bot hoon (Webhook Mode).\nAb mujhse koi bhi sawal puchiye!"
    )

@bot.message_handler(func=lambda msg: True)
def ai_reply(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        
        reply_text = response.text
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                bot.reply_to(message, reply_text[i:i+4000])
        else:
            bot.reply_to(message, reply_text)
            
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

# --- Webhook Routes (No 409 Conflict Ever!) ---
@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def home():
    return "AI Bot is running 24/7 with Webhook!", 200

if __name__ == "__main__":
    # Purana conflict hatakar naya Webhook set karna
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
