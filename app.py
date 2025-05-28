from flask import Flask, render_template, request, send_from_directory
import os
import yt_dlp

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# 👇 هذا هو السطر المهم!
@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    download_url = None

    if request.method == 'POST':
        url = request.form['url']
        try:
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title).70s.%(ext)s'),
                'format': 'mp4',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                final_name = os.path.basename(filename)
                download_url = f'/downloads/{final_name}'
        except Exception as e:
            error = str(e)

    return render_template('index.html', error=error, download_url=download_url)

if __name__ == '__main__':
    app.run(debug=True)
