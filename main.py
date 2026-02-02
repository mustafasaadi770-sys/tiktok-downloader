import telebot
import requests
import os
from threading import Thread
from flask import Flask
from moviepy.editor import VideoFileClip

# --- 1. تشغيل سيرفر وهمي لإبقاء البوت حياً على Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوت بالتوكن الخاص بك ---
TOKEN = '8292214871:AAHSXs7jK95MQQVtQ1Sc4TCSNbMDuuE8h-w'
MY_RIGHTS = "@1.3vv"

bot = telebot.TeleBot(TOKEN)

# --- 3. دالة معالجة الفيديو (قص الأطراف لإخفاء العلامة) ---
@bot.message_handler(content_types=['video'])
def handle_uploaded_video(message):
    try:
        wait_msg = bot.reply_to(message, f"⏳ جاري معالجة الفيديو وإضافة بصمتك {MY_RIGHTS}...")
        
        # تحميل الفيديو من تليجرام
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_path = "input_temp.mp4"
        output_path = "output_clean.mp4"
        
        with open(input_path, 'wb') as f:
            f.write(downloaded_file)

        # عملية القص (Crop) لإزالة العلامات المائية من الأطراف
        clip = VideoFileClip(input_path)
        w, h = clip.size
        # نقص 10% من الأعلى و 10% من الأسفل
        final_video = clip.crop(y1=h*0.1, y2=h*0.9) 
        
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

        # إرسال الفيديو النهائي
        with open(output_path, 'rb') as v:
            bot.send_video(message.chat.id, v, caption=f"تمت المعالجة بنجاح ✅\nبواسطة: {MY_RIGHTS}")

        # تنظيف الملفات المؤقتة
        clip.close()
        final_video.close()
        os.remove(input_path)
        os.remove(output_path)
        bot.delete_message(message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء المعالجة: {str(e)}")

# --- 4. التحميل من روابط تيك توك ---
@bot.message_handler(func=lambda m: m.text and "tiktok.com" in m.text)
def handle_tiktok(message):
    url = message.text.strip()
    api_url = f"https://www.tikwm.com/api/?url={url}"
    try:
        res = requests.get(api_url).json()
        if res.get('code') == 0:
            video_url = res['data']['play'] # فيديو بدون علامة مائية من المصدر
            bot.send_video(message.chat.id, video_url, caption=f"تم التحميل بنجاح 🎬\n{MY_RIGHTS}")
        else:
            bot.reply_to(message, "❌ فشل جلب الفيديو من الرابط.")
    except:
        bot.reply_to(message, "❌ حدث خطأ في الاتصال بالخدمة.")

# --- 5. تشغيل البوت ---
if __name__ == "__main__":
    keep_alive()
    print("🚀 البوت انطلق الآن...")
    bot.infinity_polling(skip_pending=True)
