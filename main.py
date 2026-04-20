import os
import telebot
import google.generativeai as genai

# အချက်အလက်များကို Environment Variables မှ ရယူခြင်း
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Gemini AI ကို Setup လုပ်ခြင်း
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Telegram Bot ကို Setup လုပ်ခြင်း
bot = telebot.TeleBot(BOT_TOKEN)

# /start command အတွက်
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! ကျွန်တော်က Gemini AI Bot ပါ။ ဘာကူညီပေးရမလဲခင်ဗျာ?")

# စာသားများအားလုံးကို AI ဖြင့် ပြန်လည်ဖြေကြားခြင်း
@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        # AI ဆီသို့ စာသားပို့ခြင်း
        response = model.generate_content(message.text)
        # AI ပြန်ဖြေသည့်စာသားကို Telegram သို့ ပြန်ပို့ခြင်း
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "ခဏလေးနော်၊ အမှားတစ်ခုရှိနေလို့ပါ။")

# Bot ကို စတင် Run ခြင်း
print("Bot is running...")
bot.infinity_polling()
