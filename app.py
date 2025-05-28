from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os
import uuid

app = Flask(__name__)

# تأكد مجلد التنزيل موجود
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    download_url = None
    if request.method == 'POST':
        video_url = request.form.get('url')
        if video_url:
            try:
                # اسم عشوائي للفيديو لتجنب التعارض
                filename = str(uuid.uuid4()) + '.mp4'
                filepath = os.path.join(DOWNLOAD_FOLDER, filename)

                ydl_opts = {
                    'outtmpl': filepath,
                    'format': 'mp4',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                # رابط التحميل بعد النجاح
                download_url = f'/downloads/{filename}'
            except Exception as e:
                return render_template("index.html", error=str(e))

    return render_template("index.html", download_url=download_url)

# للسماح بتحميل الملفات من مجلد downloads
@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
