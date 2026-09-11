from flask import Flask, render_template, request, jsonify, send_from_directory
import mysql.connector
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
import sys


# =========================================================
# WINDOWS UTF-8
# =========================================================

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# BASE DIRECTORY + .ENV
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

# Load .env from the same folder as app.py
load_dotenv(ENV_FILE, override=True)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}


# =========================================================
# DATABASE CONFIGURATION CHECK
# =========================================================

print("=" * 60)
print("DATABASE CONFIGURATION")
print("=" * 60)

print("ENV FILE:", ENV_FILE)
print("ENV EXISTS:", ENV_FILE.exists())

print("HOST:", DB_CONFIG["host"])
print("PORT:", DB_CONFIG["port"])
print("USER:", DB_CONFIG["user"])
print("DATABASE:", DB_CONFIG["database"])
print("PASSWORD SET:", bool(DB_CONFIG["password"]))

print("=" * 60)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    try:

        # Check required settings
        if not DB_CONFIG["host"]:
            raise ValueError("DB_HOST is missing in .env")

        if not DB_CONFIG["user"]:
            raise ValueError("DB_USER is missing in .env")

        if not DB_CONFIG["password"]:
            raise ValueError("DB_PASSWORD is missing in .env")

        if not DB_CONFIG["database"]:
            raise ValueError("DB_NAME is missing in .env")


        # Connect to Aiven MySQL
        conn = mysql.connector.connect(

            host=DB_CONFIG["host"],

            port=DB_CONFIG["port"],

            user=DB_CONFIG["user"],

            password=DB_CONFIG["password"],

            database=DB_CONFIG["database"],

            connection_timeout=15
        )


        print("Aiven MySQL connected successfully!")

        return conn


    except Exception as e:

        print("=" * 60)
        print("DATABASE CONNECTION ERROR")
        print("=" * 60)
        print(repr(e))
        print("=" * 60)

        raise


# =========================================================
# AUDIO FILE SERVE
# =========================================================

@app.route("/static/audio/<filename>")
def serve_audio(filename):

    audio_dir = os.path.join(
        app.root_path,
        "static",
        "audio"
    )


    if not os.path.exists(audio_dir):

        return jsonify({

            "success": False,

            "error": "Audio directory not found"

        }), 404


    ext = filename.rsplit(".", 1)[-1].lower()


    if ext == "mp4":

        mime = "audio/mp4"

    elif ext == "wav":

        mime = "audio/wav"

    elif ext == "ogg":

        mime = "audio/ogg"

    elif ext == "webm":

        mime = "audio/webm"

    else:

        mime = "audio/mpeg"


    return send_from_directory(

        audio_dir,

        filename,

        mimetype=mime

    )


# =========================================================
# TEST DATABASE CONNECTION
# =========================================================

@app.route("/test-db")
def test_db():

    conn = None
    cursor = None


    try:

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute("SELECT 1")

        result = cursor.fetchone()


        return jsonify({

            "success": True,

            "message": "Aiven MySQL Connected Successfully!",

            "result": result

        })


    except Exception as e:

        print("ACTUAL AIVEN ERROR:", repr(e))


        return jsonify({

            "success": False,

            "error": repr(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    return render_template("index.html")


# =========================================================
# CONTACT API
# =========================================================

@app.route("/api/contact", methods=["POST"])
def contact():

    conn = None
    cursor = None


    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "error": "Invalid request data"

            }), 400


        name = data.get("name", "").strip()

        email = data.get("email", "").strip()

        message = data.get("message", "").strip()


        # Required fields
        if not name or not email or not message:

            return jsonify({

                "success": False,

                "error": "All fields required"

            }), 400


        # Connect database
        conn = get_db()

        cursor = conn.cursor()


        # Insert contact message
        cursor.execute(

            """
            INSERT INTO contacts
            (name, email, message, created_at)
            VALUES (%s, %s, %s, %s)
            """,

            (

                name,

                email,

                message,

                datetime.now()

            )

        )


        # Save changes
        conn.commit()


        print("Contact message saved to Aiven MySQL!")


        return jsonify({

            "success": True,

            "message": "Message sent successfully!"

        })


    except Exception as e:

        if conn:

            conn.rollback()


        print("CONTACT DATABASE ERROR:", repr(e))


        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# =========================================================
# PAGE VIEW TRACKING
# =========================================================

@app.route("/api/views", methods=["POST"])
def track_view():

    conn = None
    cursor = None


    try:

        # Connect database
        conn = get_db()

        cursor = conn.cursor()


        # Insert page view
        cursor.execute(

            """
            INSERT INTO page_views
            (visited_at, ip)
            VALUES (%s, %s)
            """,

            (

                datetime.now(),

                request.remote_addr

            )

        )


        # Save changes
        conn.commit()


        print("Page view saved to Aiven MySQL!")


        return jsonify({

            "success": True,

            "message": "Page view saved successfully!"

        })


    except Exception as e:

        if conn:

            conn.rollback()


        print("PAGE VIEW DATABASE ERROR:", repr(e))


        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )