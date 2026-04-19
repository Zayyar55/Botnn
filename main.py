import os
import threading
import requests
import random
from datetime import datetime
import pytz
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, ChatMemberHandler, filters

# --- CONFIGURATION ---
GROQ_API_KEY = "gsk_EmKkH2tf (မင်းရဲ့ Key ထည့်ပါ)"
TG_TOKEN = "8774327296:AAHfzzOTEh0eShFmCLH78fTHR3XVNgk5qFM"
BAD_WORDS = ["လီး", "ငါလိုးမသား", "မင်းမေစပ", "စပစား", "စောက်ကောင်", "ယီးပဲ", "မအေလိုး", "ခွေးမသား", "ဖာသယ်"]

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Moki is Ready!")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def get_time_context():
    tz = pytz.timezone('Asia/Yangon')
    now = datetime.now(tz)
    hour = now.hour
    if 5 <= hour < 10: return "အခုမှ အိပ်ယာနိုးလို့ လိုင်းတက်တာ။ Morning ပါ အသဲလေးတို့ ☕"
    elif 10 <= hour < 17: return "တစ်ယောက်ထဲ ပျင်းလို့ လိုင်းသုံးနေတာ။ 🌻"
    elif 17 <= hour < 22: return "TikTok ကြည့်နေတာ။ 📱"
    else: return "ညဉ့်နက်နေပြီလေ၊ အိပ်တော့မလို့။ 😴"

def query_ai(text):
    time_info = get_time_context()
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # AI ကို ပေးတဲ့ Instruction ကို အရမ်းရှင်းအောင် ပြောင်းလိုက်တယ်
    system_prompt = f"""
    မင်းက Moki၊ Channel Admin မိန်းကလေး။ 
    - User မေးတာကို အရင်ဆုံး တိုက်ရိုက်ဖြေပါ။ 
    - နေကောင်းလားမေးရင် 'ကောင်းပါတယ်ရှင်' လို့ပဲ ဖြေပါ။
    - ဘာလုပ်နေလဲမေးရင် ဒီအချက်ကို သုံးပါ: {time_info}
    - စကားပြောရင် Emoji (✨, ❤️, 😊) လေးတွေ ထည့်သုံးပါ။
    - မမေးတဲ့အချက်တွေကို လျှောက်မပြောပါနဲ့။
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.5 # AI မရောင်အောင် လျှော့ထားတယ်
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.json()['choices'][0]['message']['content']
    except: return "လိုင်းမကောင်းလို့ ခဏလေးနော် ❤️"

# လူသစ်ဝင်လာမှသာ နှုတ်ဆက်မယ့် function
async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # status က member ဖြစ်သွားမှသာ (ဝင်လာမှသာ) ပို့မယ်
    if update.chat_member.new_chat_member.status == "member":
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="အချောလေးတစ်ယောက် ရောက်နေတယ်နော် ✨ အေးဆေးကြည့်သွားပါဦးရှင် ❤️"
        )

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_text = update.message.text
    chat_id = update.effective_chat.id

    # ၁။ ဆဲစာ စစ်မယ်
    if any(word in user_text for word in BAD_WORDS):
        await update.message.delete()
        await context.bot.send_message(chat_id=chat_id, text="အပြောအဆို ဆင်ခြင်ပေးပါနော် ✨")
        return

    # ၂။ Link စစ်မယ်
    if "http" in user_text or "t.me/" in user_text:
        await context.bot.send_message(chat_id=chat_id, text="Link လာချသွားတယ်နော် ⚠️ Owner ကြည့်ပြီးမှ ဆုံးဖြတ်ပါလိမ့်မယ် ✨")
        return

    # ၃။ AI စကားပြန်ခြင်း (ဒီမှာ User မေးတာကိုပဲ ပို့ပေးမှာပါ)
    ai_response = query_ai(user_text)
    await update.message.reply_text(ai_response)

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    app = ApplicationBuilder().token(TG_TOKEN).build()
    
    # Handler တွေကို သေချာခွဲထားတယ်
    app.add_handler(ChatMemberHandler(welcome_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.CHAT, handle_all_messages))
    
    print("Moki Bot is running...")
    app.run_polling()
