# 🚀 Portfolio — Flask + MySQL + HTML/CSS/JS

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MySQL Database
```bash
mysql -u root -p < schema.sql
```

### 3. Update DB Config in app.py
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD',   # ← change this
    'database': 'portfolio_db'
}
```

### 4. Run the App
```bash
python app.py
```

Open → http://localhost:5000

---

## Features
- ✅ Voice on hover (your voice plays when hovering over text)
- ✅ Custom animated cursor
- ✅ Dynamic skill bars
- ✅ Floating parallax cards
- ✅ Contact form saved to MySQL
- ✅ Your photo in About section (circle)
- ✅ Fully responsive

## Stack
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Backend:** Python + Flask
- **Database:** MySQL
