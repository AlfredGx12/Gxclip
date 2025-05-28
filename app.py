from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os
import uuid

app = Flask(__name__)

# مجلد التنزيل
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
                filename = str(uuid.uuid4()) + '.mp4'
                filepath = os.path.join(DOWNLOAD_FOLDER, filename)

                ydl_opts = {
                    'outtmpl': filepath,
                    'format': 'best[ext=mp4]/best',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                download_url = f'/downloads/{filename}'
            except Exception as e:
                error = str(e)

    return render_template("index.html", download_url=download_url, error=error)

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# هذا هو التعديل المهم لتشتغل على Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
