from flask import Flask, request, send_file
import yt_dlp
import os
import uuid
from flask_cors import CORS
import mimetypes

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

    headers = {
        'User-Agent': (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/116.0.0.0 Safari/537.36"
        ),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.youtube.com/',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'
    }

    ydl_opts = {
        'cookiefile': 'cookies.txt',
        'outtmpl': out_path,
        'format': 'bestaudio/best' if format_type == 'mp3' else 'best',
        'quiet': False,
        'noplaylist': True,
        'http_headers': headers,
        'geo_bypass': True,
        'verbose': True,
    }

    # 🔧 Add MP3 postprocessor
    if format_type == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    else:
        # 🔧 Ensure merged audio/video in MP4 format
        ydl_opts['merge_output_format'] = 'mp4'

    # 🔽 Perform download
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info)
        if format_type == 'mp3':
            filename = os.path.splitext(filename)[0] + ".mp3"

    # 🔎 Check if file exists
    if not os.path.exists(filename):
        return "Download failed on server", 500

    # 📦 Get proper MIME type
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = 'application/octet-stream'

    # ✅ Return file with proper headers
    return send_file(
        filename,
        mimetype=mime_type,
        as_attachment=True,
        download_name=os.path.basename(filename)
    )

@app.route('/debug-cookies')
def debug_cookies():
    try:
        with open('cookies.txt', 'r') as f:
            content = f.read(500)  # read first 500 chars to avoid huge output
        return "<pre>" + content + "</pre>"
    except Exception as e:
        return f"Error reading cookies.txt: {e}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
