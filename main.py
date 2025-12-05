"""
Flask Single-File Website
File name: flask_website.py

Features:
- Home, About, Contact pages (Bootstrap layout)
- Contact form saves messages to a local SQLite database
- Simple admin view to list messages (protected by ADMIN_KEY env var)
- Self-contained: templates are rendered with render_template_string

Run:
1. python -m venv venv
2. source venv/bin/activate    # on Windows: venv\Scripts\activate
3. pip install Flask
4. export ADMIN_KEY=your_secret   # on Windows: set ADMIN_KEY=your_secret
5. python flask_website.py
6. Open http://127.0.0.1:5000

Note: This is a minimal example intended for learning/development only. Do not use ADMIN_KEY via query strings in production.
"""

from flask import Flask, request, redirect, url_for, render_template_string, g, abort
import sqlite3
import os
from datetime import datetime

DATABASE = 'messages.db'
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'admin123')  # change before real use

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', 'dev-secret')

# -------------------------
# Database helpers
# -------------------------

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# -------------------------
# Templates (inline for single-file convenience)
# -------------------------

base_template = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title or 'My Flask Site' }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body { padding-top: 56px; }
      .hero { padding: 60px 0; }
    </style>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
      <div class="container">
        <a class="navbar-brand" href="{{ url_for('home') }}">My Flask Site</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarsExampleDefault" aria-controls="navbarsExampleDefault" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarsExampleDefault">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item"><a class="nav-link" href="{{ url_for('home') }}">Home</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('about') }}">About</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('contact') }}">Contact</a></li>
          </ul>
        </div>
      </div>
    </nav>

    <main class="container">
      {% block content %}{% endblock %}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
"""

home_template = """
{% extends 'base' %}
{% block content %}
  <div class="hero text-center">
    <h1 class="display-5">Welcome to My Flask Site</h1>
    <p class="lead">This is a simple single-file Flask website example with a contact form.</p>
    <p><a href="{{ url_for('contact') }}" class="btn btn-primary btn-lg">Contact Us</a></p>
  </div>

  <div class="row">
    <div class="col-md-6">
      <h3>Features</h3>
      <ul>
        <li>Bootstrap layout</li>
        <li>Contact form saved to SQLite</li>
        <li>Minimal admin to view messages</li>
      </ul>
    </div>
    <div class="col-md-6">
      <h3>Quick Start</h3>
      <p>Run the file and visit <code>http://127.0.0.1:5000</code>.</p>
    </div>
  </div>
{% endblock %}
"""

about_template = """
{% extends 'base' %}
{% block content %}
  <div class="py-4">
    <h2>About</h2>
    <p>This demo site was created to show how to build a small Python/Flask website in a single file. Use it as a starting point for learning or prototyping.</p>
  </div>
{% endblock %}
"""

contact_template = """
{% extends 'base' %}
{% block content %}
  <div class="py-4">
    <h2>Contact Us</h2>
    {% if success %}
      <div class="alert alert-success">Thanks! Your message has been received.</div>
    {% endif %}

    <form method="post" action="{{ url_for('contact') }}">
      <div class="mb-3">
        <label class="form-label">Name</label>
        <input type="text" class="form-control" name="name" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input type="email" class="form-control" name="email" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Subject</label>
        <input type="text" class="form-control" name="subject">
      </div>
      <div class="mb-3">
        <label class="form-label">Message</label>
        <textarea class="form-control" name="message" rows="5" required></textarea>
      </div>
      <button class="btn btn-primary" type="submit">Send Message</button>
    </form>
  </div>
{% endblock %}
"""

messages_template = """
{% extends 'base' %}
{% block content %}
  <div class="py-4">
    <h2>Messages</h2>
    {% if messages | length == 0 %}
      <p>No messages yet.</p>
    {% else %}
      <table class="table table-striped">
        <thead>
          <tr><th>ID</th><th>Name</th><th>Email</th><th>Subject</th><th>Message</th><th>Received</th></tr>
        </thead>
        <tbody>
          {% for m in messages %}
            <tr>
              <td>{{ m.id }}</td>
              <td>{{ m.name }}</td>
              <td>{{ m.email }}</td>
              <td>{{ m.subject }}</td>
              <td style="max-width:400px;">{{ m.message }}</td>
              <td>{{ m.created_at }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% endif %}
  </div>
{% endblock %}
"""

# -------------------------
# Route bindings
# -------------------------

# Jinja loader hack: allow using our inline templates as if they were files
from jinja2 import DictLoader
app.jinja_loader = DictLoader({
    'base': base_template,
    'home.html': home_template,
    'about.html': about_template,
    'contact.html': contact_template,
    'messages.html': messages_template,
})


@app.before_first_request
def setup():
    init_db()


@app.route('/')
def home():
    return render_template_string(home_template)


@app.route('/about')
def about():
    return render_template_string(about_template)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    success = False
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject') or ''
        message = request.form.get('message')
        if not (name and email and message):
            abort(400, 'Missing fields')
        db = get_db()
        db.execute('INSERT INTO messages (name, email, subject, message, created_at) VALUES (?, ?, ?, ?, ?)',
                   (name, email, subject, message, datetime.utcnow().isoformat()))
        db.commit()
        success = True
    return render_template_string(contact_template, success=success)


@app.route('/admin/messages')
def admin_messages():
    # Very simple auth: require ?key=ADMIN_KEY or match env var
    key = request.args.get('key', '')
    if key != ADMIN_KEY:
        abort(403, 'Forbidden')
    db = get_db()
    cur = db.execute('SELECT * FROM messages ORDER BY id DESC')
    msgs = cur.fetchall()
    return render_template_string(messages_template, messages=msgs)


if __name__ == '__main__':
    # create DB if missing
    if not os.path.exists(DATABASE):
        with app.app_context():
            init_db()
    app.run(debug=True)
