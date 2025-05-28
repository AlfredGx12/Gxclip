from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
app = Flask(__name__)

# مسار مجلد التحميلات
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# دالة لتحديث ملف الكوكيات تلقائياً
def update_cookies():
    print("جاري تحديث ملف الكوكيات...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 1. الانتقال إلى YouTube وتسجيل الدخول (مثال)
        driver.get("https://www.youtube.com")
        time.sleep(2)
        
        # 2. هنا يمكنك إضافة خطوات تسجيل الدخول الآلي إذا كان لديك بيانات حساب
        # driver.find_element(...).click()
        
        # 3. الحصول على الكوكيات وتحديث الملف
        cookies = driver.get_cookies()
        with open('cookies.txt', 'w') as f:
            for cookie in cookies:
                f.write(f"{cookie['name']}={cookie['value']}\n")
        
        print("تم تحديث ملف الكوكيات بنجاح!")
    except Exception as e:
        print(f"خطأ في تحديث الكوكيات: {str(e)}")
    finally:
        driver.quit()

# دالة لتحميل فيديو يوتيوب مع التعامل مع الكوكيز
def download_youtube_video(url):
    try:
        # خيارات yt-dlp مع الكوكيات
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except yt_dlp.utils.DownloadError as e:
        print(f"خطأ في التحميل: {str(e)}")
        # إذا فشلت المحاولة الأولى، نقوم بتحديث الكوكيات والمحاولة مرة أخرى
        update_cookies()
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return filename
        except Exception as e:
            print(f"فشلت المحاولة الثانية: {str(e)}")
            return None
    except Exception as e:
        print(f"خطأ غير متوقع: {str(e)}")
        return None

# دالة لتحميل من إنستجرام
def download_instagram_video(url):
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"خطأ في تحميل إنستجرام: {str(e)}")
        return None

# دالة لتحميل من تيك توك
def download_tiktok_video(url):
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"خطأ في تحميل تيك توك: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['url']
    
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

@app.route('/download_file/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(DOWNLOAD_FOLDER, filename),
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    # تحديث الكوكيات عند بدء التشغيل
    update_cookies()
    app.run(debug=True)
