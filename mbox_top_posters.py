import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'top_posters.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='',
    PASSWORD=''
))

app.config.from_envvar('TOP_POSTER_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with db:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())

def test_data():
    with app.app_context():
        db = get_db()
        with db:
            for i in range(4):
                db.execute('insert into posters values (null, "Joseph", 100)')
        
@app.route('/')
@app.route('/<date_range>/')
def get_top_posters(date_range="month"):
    if date_range not in ["month", "semester", "year", "all_time"]:
        abort(404)
    db = get_db()
    query = 'select id, name, count from ' + date_range + ' order by id asc'
    cur = db.execute(query)
    posters = cur.fetchall()
    return render_template('layout.html', posters=posters, active_page=date_range)

if __name__ == '__main__':
    app.run()
