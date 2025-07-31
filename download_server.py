from flask import Flask, request, send_file
import yt_dlp
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download')
def download():
    video_url = request.args.get('url')
    format_type = request.args.get('format', 'mp3')

    if not video_url or format_type not in ('mp3', 'mp4'):
        return "Invalid request", 400

    uid = str(uuid.uuid4())
    out_path = f"/tmp/{uid}.%(ext)s"

    ydl_opts = {
        'cookiefile': 'cookies.txt',  # Add your cookies.txt path here
        'outtmpl': out_path,
        'format': 'bestaudio/best' if format_type == 'mp3' else 'best',
        'quiet': True,
        'noplaylist': True
    }

    if format_type == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info)
        if format_type == 'mp3':
            filename = os.path.splitext(filename)[0] + ".mp3"

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
