from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'alumni.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_to_a_random_secret_in_production'
app.config['DATABASE'] = DB_PATH

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False, commit=False):
    cur = get_db().execute(query, args)
    if commit:
        get_db().commit()
        cur.close()
        return None
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    if not os.path.exists(app.config['DATABASE']):
        with app.app_context():
            schema = open(os.path.join(BASE_DIR, 'schema.sql')).read()
            get_db().executescript(schema)
            get_db().commit()
            print('Initialized database.')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    posts = query_db('SELECT p.id,p.title,p.body,p.created_at,u.name FROM posts p JOIN users u ON p.user_id=u.id ORDER BY p.created_at DESC LIMIT 6')
    events = query_db('SELECT * FROM events ORDER BY date DESC LIMIT 6')
    return render_template('index.html', posts=posts, events=events)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        year = request.form.get('year','')
        company = request.form.get('company','')
        bio = request.form.get('bio','')
        if not name or not email or not password:
            flash('Name, email and password are required', 'danger')
            return redirect(url_for('register'))
        existing = query_db('SELECT * FROM users WHERE email=?', [email], one=True)
        if existing:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        pw_hash = generate_password_hash(password)
        query_db('INSERT INTO users (name,email,password_hash,year,company,bio) VALUES (?,?,?,?,?,?)', [name,email,pw_hash,year,company,bio], commit=True)
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE email=?', [email], one=True)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = query_db('SELECT * FROM users WHERE id=?', [session['user_id']], one=True)
    posts = query_db('SELECT * FROM posts WHERE user_id=? ORDER BY created_at DESC', [session['user_id']])
    events = query_db('SELECT * FROM events ORDER BY date DESC LIMIT 5')
    return render_template('dashboard.html', user=user, posts=posts, events=events)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = query_db('SELECT * FROM users WHERE id=?', [user_id], one=True)
    if not user:
        flash('User not found', 'warning')
        return redirect(url_for('index'))
    return render_template('profile.html', user=user)

@app.route('/create_post', methods=['GET','POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title'].strip()
        body = request.form['body'].strip()
        now = datetime.utcnow().isoformat()
        query_db('INSERT INTO posts (user_id,title,body,created_at) VALUES (?,?,?,?)', [session['user_id'],title,body,now], commit=True)
        flash('Post created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_post.html')

@app.route('/posts')
def posts():
    posts = query_db('SELECT p.id,p.title,p.body,p.created_at,u.name FROM posts p JOIN users u ON p.user_id=u.id ORDER BY p.created_at DESC')
    return render_template('posts.html', posts=posts)

@app.route('/create_event', methods=['GET','POST'])
@login_required
def create_event():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        date = request.form['date']
        location = request.form.get('location','')
        query_db('INSERT INTO events (user_id,title,description,date,location) VALUES (?,?,?,?,?)', [session['user_id'],title,description,date,location], commit=True)
        flash('Event created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_event.html')

@app.route('/events')
def events():
    events = query_db('SELECT e.*, u.name FROM events e JOIN users u ON e.user_id=u.id ORDER BY date DESC')
    return render_template('events.html', events=events)

@app.route('/rsvp/<int:event_id>', methods=['POST'])
@login_required
def rsvp(event_id):
    existing = query_db('SELECT * FROM rsvps WHERE event_id=? AND user_id=?', [event_id, session['user_id']], one=True)
    if existing:
        flash('You have already RSVPed', 'info')
    else:
        query_db('INSERT INTO rsvps (event_id,user_id) VALUES (?,?)', [event_id, session['user_id']], commit=True)
        flash('RSVP successful', 'success')
    return redirect(url_for('events'))

@app.route('/search')
def search():
    q = request.args.get('q','').strip()
    members = []
    if q:
        likeq = f"%{q}%"
        members = query_db('SELECT * FROM users WHERE name LIKE ? OR company LIKE ? OR year LIKE ? LIMIT 50', [likeq,likeq,likeq])
    return render_template('search.html', members=members, q=q)

@app.route('/mentorship', methods=['GET','POST'])
@login_required
def mentorship():
    if request.method == 'POST':
        topic = request.form['topic'].strip()
        role = request.form['role']  # mentor or mentee
        query_db('INSERT INTO mentorships (user_id,topic,role,created_at) VALUES (?,?,?,?)', [session['user_id'],topic,role,datetime.utcnow().isoformat()], commit=True)
        flash('Mentorship interest saved', 'success')
        return redirect(url_for('mentorship'))
    mentors = query_db('SELECT m.*, u.name, u.company, u.year FROM mentorships m JOIN users u ON m.user_id=u.id WHERE m.role="mentor" ORDER BY m.created_at DESC')
    mentees = query_db('SELECT m.*, u.name, u.company, u.year FROM mentorships m JOIN users u ON m.user_id=u.id WHERE m.role="mentee" ORDER BY m.created_at DESC')
    return render_template('mentorship.html', mentors=mentors, mentees=mentees)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
