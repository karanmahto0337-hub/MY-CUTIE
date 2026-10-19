import os
import requests
from flask import Flask, request
import telebot

# 1. Apna Telegram Bot Token daalein
BOT_TOKEN = "8813016822:AAFuSYJCWV9Tw0e0J_29vGhf63oqujOU7OQ".strip()

# 2. Yahan apni Groq Key (gsk_... wali) daalein
AI_API_KEY = "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".strip()

# 3. Apna Render wala Link (https://...onrender.com) yahan daalein
RENDER_URL = "https://my-cutie.onrender.com/".strip().rstrip('/')

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

def get_working_model(headers):
    # Groq se puchna ki kaunse AI models active hain
    try:
        r = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
        models = [m["id"] for m in r.json().get("data", [])]
        # Sabse best chat model chunna
        for preferred in ["llama-3.1-8b-instant", "llama3-8b-8192", "gemma2-9b-it"]:
            if preferred in models:
                return preferred
        # Koi bhi llama ya chat model jo active ho
        for m in models:
            if "whisper" not in m and "guard" not in m and "tts" not in m:
                return m
    except Exception:
        pass
    return "llama-3.1-8b-instant"

def ask_ai(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    active_model = get_working_model(headers)
    
    data = {
        "model": active_model,
        "messages": [
            {"role": "system", "content": "You are a helpful, smart AI assistant like ChatGPT. Reply naturally in the same language the user speaks (Hindi, Hinglish, or English)."},
            {"role": "user", "content": user_text}
        ]
    }
    res = requests.post(url, headers=headers, json=data)
    res_json = res.json()
    if "choices" in res_json:
        return res_json["choices"][0]["message"]["content"]
    else:
        return f"API Error: {res_json}"

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Namaste! 🤖 Main Super-Fast AI Bot hoon.\nMujhse koi bhi sawal puchiye, main palak jhapakte hi jawab dunga!"
    )

@bot.message_handler(func=lambda msg: True)
def ai_reply(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        reply_text = ask_ai(message.text)
        
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                bot.reply_to(message, reply_text[i:i+4000])
        else:
            bot.reply_to(message, reply_text)
            
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

# --- Webhook Routes ---
@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def home():
    return "AI Bot is running 24/7!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
