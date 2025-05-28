from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime

app = Flask(__name__)

# مسار مجلد التحميلات
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# إعداد السيلينيوم (النسخة المحسنة)
def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    try:
        # استخدام المسار الثابت لـ chromedriver المثبت في Dockerfile
        service = Service(executable_path="/usr/local/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"خطأ في إعداد السيلينيوم: {str(e)}")
        return None

# تحديث ملف الكوكيز (النسخة المحسنة)
def update_cookies():
    print("جاري تحديث ملف الكوكيات...")
    driver = setup_selenium()
    
    if not driver:
        print("فشل في تهيئة متصفح السيلينيوم")
        return False
        
    try:
        driver.get("https://www.youtube.com")
        time.sleep(10)  # زيادة وقت الانتظار
        
        cookies = driver.get_cookies()
        with open('cookies.txt', 'w', encoding='utf-8') as f:
            for cookie in cookies:
                f.write(f"{cookie['name']}={cookie['value']}\n")
        
        print("تم تحديث ملف الكوكيات بنجاح!")
        return True
    except Exception as e:
        print(f"خطأ في تحديث الكوكيات: {str(e)}")
        # إنشاء ملف كوكيز فارغ إذا فشل التحديث
        with open('cookies.txt', 'w', encoding='utf-8') as f:
            f.write("")
        return False
    finally:
        if driver:
            driver.quit()

# تحميل من يوتيوب (النسخة المحسنة)
def download_youtube_video(url):
    try:
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'retries': 3
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"خطأ في التحميل من يوتيوب: {str(e)}")
        return None

# تحميل من إنستجرام (النسخة المحسنة)
def download_instagram_video(url):
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True,
            'ignoreerrors': True,
            'retries': 3
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"خطأ في تحميل إنستجرام: {str(e)}")
        return None

# تحميل من تيك توك (النسخة المحسنة)
def download_tiktok_video(url):
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True,
            'ignoreerrors': True,
            'retries': 3
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"خطأ في تحميل تيك توك: {str(e)}")
        return None

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# معالجة التحميل (النسخة المحسنة)
@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url', '').strip()
    
    if not video_url:
        return jsonify({'error': 'الرجاء إدخال رابط الفيديو'}), 400
    
    try:
        if "youtube.com" in video_url or "youtu.be" in video_url:
            filename = download_youtube_video(video_url)
            platform = "يوتيوب"
        elif "instagram.com" in video_url:
            filename = download_instagram_video(video_url)
            platform = "إنستجرام"
        elif "tiktok.com" in video_url:
            filename = download_tiktok_video(video_url)
            platform = "تيك توك"
        else:
            return jsonify({'error': 'نوع الرابط غير مدعوم'}), 400
        
        if filename and os.path.exists(filename):
            return jsonify({
                'success': True,
                'platform': platform,
                'filename': os.path.basename(filename),
                'download_url': f'/download_file/{os.path.basename(filename)}'
            })
        else:
            return jsonify({'error': 'فشل تحميل الفيديو'}), 500
    except Exception as e:
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

# تحميل الملف
@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(DOWNLOAD_FOLDER, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'الملف غير موجود: {str(e)}'}), 404

# التشغيل الرئيسي (النسخة المحسنة)
if __name__ == '__main__':
    # تحديث الكوكيز عند بدء التشغيل (مع معالجة الأخطاء)
    try:
        update_cookies()
    except Exception as e:
        print(f"خطأ في تحديث الكوكيات عند البدء: {str(e)}")
    
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=5000, debug=False)
