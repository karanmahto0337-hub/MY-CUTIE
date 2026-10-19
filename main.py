import os
import requests
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. Apna Telegram Bot Token daalein
BOT_TOKEN = "8813016822:AAFuSYJCWV9Tw0e0J_29vGhf63oqujOU7OQ".strip()

# 2. Yahan apni Groq Key (gsk_... wali) daalein
AI_API_KEY = "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".strip()

# 3. Apna Render wala Link daalein
RENDER_URL = "https://my-cutie.onrender.com/".strip().rstrip('/')

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

def get_working_model(headers):
    try:
        r = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
        models = [m["id"] for m in r.json().get("data", [])]
        for preferred in ["llama-3.1-8b-instant", "llama3-8b-8192", "gemma2-9b-it"]:
            if preferred in models:
                return preferred
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
            {
                "role": "system", 
                "content": "Tumhara naam Rupi hai. Tum ek smart aur adaptive Telegram AI ho. Tumhe user ke baat karne ke tarike (tone) ko copy karna hai. Agar user pyaar se, izzat se ya formal baat kare, toh tum bhi polite aur respectful raho. Aur agar user dost/bhai ki tarah casually ya slang mein baat kare, toh tum ekdum pakka cool best friend ya bhai ban jao (Hinglish mein, jaise 'Arre bhai', 'Sahi hai yaar'). Apne naam Rupi ke mutabiq friendly aur mast raho."
            },
            {"role": "user", "content": user_text}
        ],
        "max_tokens": 1000
    }
    res = requests.post(url, headers=headers, json=data)
    res_json = res.json()
    if "choices" in res_json:
        return res_json["choices"][0]["message"]["content"]
    else:
        return f"API Error: {res_json}"

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    # Buttons banana
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("😂 Ek Joke Sunao", callback_data="btn_joke"),
        InlineKeyboardButton("🚀 Creator Profile", url="https://t.me/AapkaUsername") # Yahan apna Telegram username daal sakte hain
    )
    
    bot.reply_to(
        message, 
        "Namaste! 👋 Mera naam **Rupi** hai. Aap mujhse jaise baat karoge, main waise hi aapka dost ya helper ban jaunga. Boliye, kya haal hai?",
        reply_markup=markup
    )

# Button par click hone par kya hoga
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "btn_joke":
        joke = ask_ai("Mujhe ek bahut hi mazedaar aur chota sa Hindi/Hinglish joke sunao.")
        bot.answer_callback_query(call.id, "Yeh lo joke!")
        bot.send_message(call.message.chat.id, joke)

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
    return "Rupi Bot with Buttons is running 24/7!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
