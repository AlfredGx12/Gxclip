from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os
import uuid

app = Flask(__name__)

# إنشاء مجلد التحميل إذا ما كان موجود
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    download_url = None
    error = None

    if request.method == 'POST':
        video_url = request.form.get('url')
        if video_url:
            try:
                # اسم عشوائي للملف
                filename = str(uuid.uuid4())
                filepath = os.path.join(DOWNLOAD_FOLDER, f"{filename}.%(ext)s")

                ydl_opts = {
                    'outtmpl': filepath,
                    'format': 'best[ext=mp4]/best',
                    'quiet': True,
                    'no_warnings': True
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                # ابحث عن اسم الملف الناتج فعلياً
                for file in os.listdir(DOWNLOAD_FOLDER):
                    if filename in file:
                        download_url = f"/downloads/{file}"
                        break

            except Exception as e:
                error = str(e)

    return render_template("index.html", download_url=download_url, error=error)

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
