# Alumni Association Platform (Flask)

## Overview
This is a simple, interactive, and attractive alumni association platform built with Flask and SQLite.
Features:
- User registration & login (passwords hashed)
- User profiles (edit bio, graduation year, company)
- Create and browse posts (news, updates)
- Create and browse events with RSVP
- Simple mentorship match (express interest, browse mentors/mentees)
- Search members by name, company, or year
- Responsive UI using Bootstrap CDN

## Files
- `app.py` - main Flask application
- `templates/` - HTML templates (Jinja2)
- `static/style.css` - basic styling
- `static/main.js` - small client JS
- `alumni.db` - SQLite database (created on first run)
- `requirements.txt` - Python dependencies

## How to run (step-by-step)

1. Make sure Python 3.8+ is installed.
2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate     # Windows (PowerShell/CMD)
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   export FLASK_APP=app.py        # macOS/Linux
   set FLASK_APP=app.py           # Windows CMD
   $env:FLASK_APP = "app.py"      # Windows PowerShell
   flask run --host=0.0.0.0 --port=5000
   ```
   Or run directly with Python:
   ```bash
   python app.py
   ```
5. Open a browser and go to `http://127.0.0.1:5000`.

## Notes
- The app uses Bootstrap CDN for styling (internet required to fetch Bootstrap assets). If you need an offline version, I can include local copies.
- This is a minimal but extendable platform; you can add email confirmations, file uploads, OAuth, and deployment steps as next improvements.
