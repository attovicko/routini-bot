import telebot
import os
TOKEN = os.environ.get("TOKEN") # باش السيرفر يقرا التوكن مخبي
from datetime import datetime
import sqlite3
import os

TOKEN = "8919837364:AAELaIu5hUcJ_2DDmgv593S32ZONtl4gVJs"
bot = telebot.TeleBot(TOKEN)

# الروتين ديالك
ROUTINES = ["🕌 الصلاة كاملة", "🏃 رياضة", "📚 قراية", "💼 قلب على خدمة"]

# قاعدة البيانات بالتاريخ
db = sqlite3.connect("routini.db", check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS history (date TEXT, task TEXT, done INTEGER)")
db.commit()

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def get_today_status():
    cur = db.execute("SELECT task, done FROM history WHERE date=?", (today_str(),))
    return {row[0]: row[1] for row in cur.fetchall()}

def keyboard():
    status = get_today_status()
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for task in ROUTINES:
        done = status.get(task, 0)
        icon = "✅" if done else "⬜"
        markup.add(telebot.types.InlineKeyboardButton(f"{icon} {task}", callback_data=task))
    markup.add(telebot.types.InlineKeyboardButton("📊 الإحصائيات ديال الشهر", callback_data="stats"))
    return markup

@bot.message_handler(commands=['start', 'today'])
def start(message):
    bot.send_message(message.chat.id, f"روتين اليوم - {today_str()}\nكليكي باش تفاليدي:", reply_markup=keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    if call.data == "stats":
        cur = db.execute("SELECT date, COUNT(*) FROM history WHERE done=1 GROUP BY date ORDER BY date DESC LIMIT 15")
        rows = cur.fetchall()
        if not rows:
            txt = "باقي ما بديتيش، يالاه نبداو اليوم!"
        else:
            txt = "📊 آخر 15 يوم:\n"
            for d, c in rows:
                txt += f"{d}: {c}/{len(ROUTINES)} { '🔥' if c==len(ROUTINES) else ''}\n"
        bot.send_message(call.message.chat.id, txt)
        return

    # فاليدا تاسك
    task = call.data
    status = get_today_status()
    new_val = 0 if status.get(task,0)==1 else 1

    db.execute("INSERT OR REPLACE INTO history (date, task, done) VALUES (?,?,?)", (today_str(), task, new_val))
    # مسح القديم ودير الجديد باش ما يتكررش
    db.execute("DELETE FROM history WHERE rowid NOT IN (SELECT MAX(rowid) FROM history GROUP BY date, task)")
    db.commit()

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard())
    bot.answer_callback_query(call.id, "تم ✅" if new_val else "تحيد ❌")

# إلا بغيتي تخدمو حتى من البيسي بلا تيليگرام
def cli():
    print(f"\n--- روتين {today_str()} ---")
    status = get_today_status()
    for i, task in enumerate(ROUTINES, 1):
        print(f"{i}. {'[x]' if status.get(task) else '[ ]'} {task}")
    print("\nكتب رقم التاسك باش تفاليديه، و q للخروج")

print("البوت خدام... سير لتيليگرام وكتب /start")
bot.infinity_polling()