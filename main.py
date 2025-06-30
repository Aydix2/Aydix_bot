import os
import telebot
import requests

# دریافت توکن‌ها از محیط امن
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# تایم‌فریم‌ها برای انتخاب کاربر
user_timeframes = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
        "سلام! لطفا تایم‌فریم مورد نظر رو انتخاب کن:\n"
        "1 - 1 دقیقه\n"
        "2 - 5 دقیقه\n"
        "3 - 15 دقیقه\n"
        "4 - 1 ساعت\n"
        "مثلاً عدد 1 رو بفرست.")

@bot.message_handler(func=lambda m: m.text in ['1','2','3','4'])
def set_timeframe(message):
    tf_map = {'1': '1m', '2': '5m', '3': '15m', '4': '1h'}
    user_timeframes[message.chat.id] = tf_map[message.text]
    bot.send_message(message.chat.id, f"تایم‌فریم {tf_map[message.text]} انتخاب شد. حالا نام ارز دیجیتال (مثلاً BTC) رو بفرست.")

@bot.message_handler(func=lambda m: m.text.isalpha() and len(m.text) <= 5)
def crypto_signal(message):
    symbol = message.text.upper()
    timeframe = user_timeframes.get(message.chat.id, '1m')

    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
    try:
        res = requests.get(url)
        data = res.json()
        if "code" in data:
            bot.send_message(message.chat.id, "❌ نماد معتبر نیست یا خطا در دریافت داده.")
            return

        price = float(data['lastPrice'])
        price_change_percent = float(data['priceChangePercent'])

        # تحلیل ساده روند و سیگنال (نمونه)
        if price_change_percent > 0.3:
            signal = "📈 LONG"
            entry = price * 0.995
            target1 = price * 1.01
            target2 = price * 1.02
            stop_loss = price * 0.985
        elif price_change_percent < -0.3:
            signal = "📉 SHORT"
            entry = price * 1.005
            target1 = price * 0.99
            target2 = price * 0.98
            stop_loss = price * 1.015
        else:
            signal = "🔁 NO CLEAR SIGNAL"
            entry = target1 = target2 = stop_loss = price

        text = f"""⏰ تایم‌فریم: {timeframe}
💰 ارز: {symbol}
قیمت فعلی: ${price:.4f}
📊 تغییر 24 ساعته: {price_change_percent:.2f}%

سیگنال: {signal}
نقطه ورود: ${entry:.4f}
هدف 1: ${target1:.4f}
هدف 2: ${target2:.4f}
حد ضرر: ${stop_loss:.4f}
"""
        bot.send_message(message.chat.id, text)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطا در دریافت داده: {str(e)}")

print("🤖 ربات آماده اجراست.")
bot.polling()
