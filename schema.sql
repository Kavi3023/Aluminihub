-- Users
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  year TEXT,
  company TEXT,
  bio TEXT
);

-- Posts
CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  title TEXT,
  body TEXT,
  created_at TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Events
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  title TEXT,
  description TEXT,
  date TEXT,
  location TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- RSVPs
CREATE TABLE rsvps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id INTEGER,
  user_id INTEGER,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(event_id) REFERENCES events(id),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Mentorship interests
CREATE TABLE mentorships (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  topic TEXT,
  role TEXT,
  created_at TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
