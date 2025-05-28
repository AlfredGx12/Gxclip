from flask import Flask, render_template, request, send_file
import yt_dlp
import os
from uuid import uuid4

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    if not url:
        return "❌ الرجاء إدخال رابط.", 400

    # اسم الملف العشوائي
    file_id = str(uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.%(ext)s')

    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            if not filename.endswith('.mp4'):
                filename = filename.rsplit('.', 1)[0] + '.mp4'
    except Exception as e:
        return f"❌ خطأ: {str(e)}", 500

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
