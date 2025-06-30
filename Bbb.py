import telebot
import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

timeframes = ['1m', '5m', '15m', '1h']

def get_signal(symbol, tf):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}USDT&interval={tf}&limit=10"
        res = requests.get(url)
        if res.status_code != 200:
            return None

        data = res.json()
        closes = [float(kline[4]) for kline in data]
        last = closes[-1]
        prev = closes[-2]
        trend = "📈 صعودی" if last > prev else "📉 نزولی"

        entry = round(last, 2)
        target1 = round(entry * (1.01 if last > prev else 0.99), 2)
        target2 = round(entry * (1.02 if last > prev else 0.98), 2)
        stop = round(entry * (0.985 if last > prev else 1.015), 2)

        return {
            "tf": tf,
            "trend": trend,
            "entry": entry,
            "target1": target1,
            "target2": target2,
            "stop": stop
        }
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "سلام آیدا جان! 🌟\n"
        "اسم ارز دیجیتال رو انگلیسی بفرست (مثل BTC, ETH, SOL)\n"
        "تا قیمت و سیگنال تایم‌فریم‌های 1m, 5m, 15m, 1h رو بدم.")

@bot.message_handler(func=lambda m: True)
def handle_symbol(message):
    symbol = message.text.strip().upper()
    reply = f"📊 تحلیل ارز **{symbol}**:\n\n"
    ok = False
    for tf in timeframes:
        sig = get_signal(symbol, tf)
        if sig:
            ok = True
            reply += (
                f"⏱ تایم‌فریم {sig['tf']}:\n"
                f"{sig['trend']}\n"
                f"📌 ورود: {sig['entry']}\n"
                f"🎯 تارگت ۱: {sig['target1']}\n"
                f"🎯 تارگت ۲: {sig['target2']}\n"
                f"🛑 حد ضرر: {sig['stop']}\n\n"
            )
    if not ok:
        bot.send_message(message.chat.id, "❌ نماد معتبر نیست یا خطا در دریافت داده.")
    else:
        bot.send_message(message.chat.id, reply, parse_mode="Markdown")

print("🤖 ربات آماده اجراست...")
bot.polling()
