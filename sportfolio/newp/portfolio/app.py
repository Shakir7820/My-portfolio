from flask import Flask, render_template, request, jsonify, send_from_directory
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)

# ── Audio file ko sahi MIME type ke saath serve karo ──
# .mp4 audio ka MIME type audio/mp4 hona chahiye
@app.route('/static/audio/<filename>')
def serve_audio(filename):
    audio_dir = os.path.join(app.root_path, 'static', 'audio')
    ext = filename.rsplit('.', 1)[-1].lower()
    mime = 'audio/mp4' if ext == 'mp4' else 'audio/mpeg'
    return send_from_directory(audio_dir, filename, mimetype=mime)

# MySQL Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shakir@7820',  
    'database': 'portfolio_db'
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    name    = data.get('name', '')
    email   = data.get('email', '')
    message = data.get('message', '')

    if not all([name, email, message]):
        return jsonify({'success': False, 'error': 'All fields required'}), 400

    conn = get_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO contacts (name, email, message, created_at) VALUES (%s, %s, %s, %s)",
                (name, email, message, datetime.now())
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Message sent!'})
        except Exception:
            pass
    return jsonify({'success': True, 'message': 'Message received!'})

@app.route('/api/views', methods=['POST'])
def track_view():
    conn = get_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO page_views (visited_at, ip) VALUES (%s, %s)",
                (datetime.now(), request.remote_addr)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            pass
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
