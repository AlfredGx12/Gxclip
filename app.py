from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.binary_location = "/usr/bin/google-chrome"
    try:
        service = Service(executable_path="/usr/local/bin/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"خطأ في إعداد السيلينيوم: {str(e)}")
        return None

def download_youtube_video(url, quality='best'):
    try:
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'retries': 3
        }

        if quality == 'audio':
            ydl_opts['format'] = 'bestaudio'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif quality == '360':
            ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
        elif quality == '720':
            ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        else:
            ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            print("🎬 تم حفظ الفيديو في:", filename)
            return filename
    except Exception as e:
        print(f"❌ خطأ في التحميل: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url', '').strip()
    quality = request.form.get('quality', 'best').strip()
    if not url:
        return jsonify({'error': 'الرجاء إدخال رابط الفيديو'}), 400

    try:
        filename = download_youtube_video(url, quality)
        if filename and os.path.exists(filename):
            return jsonify({'success': True, 'download_url': f'/download_file/{os.path.basename(filename)}'})
        return jsonify({'error': 'فشل تحميل الفيديو'}), 500
    except Exception as e:
        import traceback
        print("❌ استثناء أثناء التحميل:")
        traceback.print_exc()
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name=filename)
    return jsonify({'error': 'الملف غير موجود'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
