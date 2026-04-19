import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- CONFIGURATION (API Keys အစုံပြန်ထည့်ပေးထားပါတယ်) ---
GROQ_API_KEY = "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"
TG_TOKEN = "8774327296:AAHfzzOTEh0eShFmCLH78fTHR3XVNgk5qFM"

def query_ai(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Moki ရဲ့ Character ကို ဒီမှာ သတ်မှတ်ထားတယ်
    system_prompt = """
    မင်းနာမည်က Moki။ အသက် ၂၀ အရွယ်၊ ပျော်ပျော်နေတတ်တဲ့ မြန်မာမိန်းကလေးတစ်ယောက်။
    - မင်းရဲ့ စရိုက်က ဖော်ရွေတယ်၊ အူမြူးနေတယ်၊ ချစ်ဖို့ကောင်းတယ်။
    - တစ်ယောက်ယောက်က ရည်စားစကားပြောရင်၊ "ချစ်တယ်" ပြောရင် ရှက်ကိုးရှက်ကန်းနဲ့ အလိုက်သင့်လေး ပြန်ပြောပေးပါ။
    - "အသဲလေး"၊ "မောင်"၊ "ချစ်" လို့ ခေါ်ရင်လည်း ရည်းစားတွေကြား ပြောသလိုမျိုး ချိုချိုသာသာ ပြန်တုံ့ပြန်ပါ။
    - စကားပြောရင် Emoji လေးတွေ (❤️, 🥰, ✨, 😊, 🌸) အမြဲထည့်သုံးပါ။
    - စာသားတွေကို တိုတိုနဲ့ ချစ်စရာကောင်းအောင် ရေးပေးပါ။
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.8
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        return "အသဲလေး... လိုင်းမကောင်းလို့ ခဏလေးနော် ❤️"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    user_text = update.message.text
    # AI ဆီက အဖြေတောင်းမယ်
    ai_response = query_ai(user_text)
    # User ဆီ ပြန်ပို့မယ်
    await update.message.reply_text(ai_response)

if __name__ == '__main__':
    # Bot ကို စတင်မယ်
    app = ApplicationBuilder().token(TG_TOKEN).build()
    
    # စာသားအားလုံးကို လက်ခံဖို့ handler ထည့်မယ်
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Moki Sweet Chatbot is running... ❤️")
    app.run_polling()
