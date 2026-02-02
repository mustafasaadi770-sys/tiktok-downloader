import telebot
import requests
import os
from threading import Thread
from flask import Flask
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# --- 1. سيرفر الوهمي لـ Render ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
def keep_alive(): Thread(target=run).start()

# --- 2. الإعدادات ---
TOKEN = '8292214871:AAHSXs7jK95MQQVtQ1Sc4TCSNbMDuuE8h-w'
MY_RIGHTS = "@1.3vv"
bot = telebot.TeleBot(TOKEN)

def get_data(url):
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url, timeout=15).json()
        return res['data'] if res.get('code') == 0 else None
    except: return None

# --- 3. ميزة القص وإخفاء العلامة المائية للفيديوهات المرفوعة ---
@bot.message_handler(content_types=['video'])
def handle_uploaded_video(message):
    try:
        wait_msg = bot.reply_to(message, "⏳ جاري قص أطراف الفيديو وإضافة بصمتك...")
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_path = "in.mp4"
        output_path = "out.mp4"
        
        with open(input_path, 'wb') as f: f.write(downloaded_file)

        # المعالجة
        clip = VideoFileClip(input_path)
        w, h = clip.size

        # عملية القص (إزالة 10% من الأعلى والأسفل)
        # هذا يخفي معظم العلامات المائية المتحركة
        clipped = clip.crop(y1=h*0.1, y2=h*0.9) 

        # إضافة بصمتك فوق الفيديو
        txt = TextClip(MY_RIGHTS, fontsize=30, color='white', font='Arial-Bold').set_duration(clip.duration).set_position(("right", "top")).margin(right=10, top=10, opacity=0)

        final = CompositeVideoClip([clipped, txt])
        final.write_videofile(output_path, codec="libx264", audio_codec="aac")

        with open(output_path, 'rb') as v:
            bot.send_video(message.chat.id, v, caption=f"تم التنظيف والحفظ بواسطة {MY_RIGHTS}")

        # تنظيف
        clip.close()
        final.close()
        os.remove(input_path)
        os.remove(output_path)
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

# --- 4. التحميل من روابط تيك توك ---
@bot.message_handler(func=lambda m: m.text and "tiktok.com" in m.text)
def handle_link(message):
    data = get_data(message.text.strip())
    if data:
        bot.send_video(message.chat.id, data['play'], caption=f"تم التحميل بدون علامة مائية ✅\n{MY_RIGHTS}")
    else:
        bot.reply_to(message, "❌ فشل التحميل")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
