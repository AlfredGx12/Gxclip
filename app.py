import yt_dlp

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict)

            return f"✅ Video downloaded: {filename}"

        except Exception as e:
            return f"❌ Error: {str(e)}"

    return render_template('index.html')
