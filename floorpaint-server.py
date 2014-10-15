"""Usage: floorpaint-server.py [--debug] DATABASE_FILE

Options:
  --debug   enable Flask debug mode and print more detailed messages
  --help    show this help message
"""
from contextlib import closing
import os
import random
import sqlite3

from docopt import docopt
from flask import abort
from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for

app = Flask(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def main_page():
    return "Hi!"

@app.route('/level/<id>')
def get_level(id):
    cur = g.db.execute('SELECT * FROM levels WHERE id=?', id)

@app.route('/level/random')
def get_random_level():
    cur = g.db.execute('SELECT * FROM levels')
    levels = cur.fetchall()
    # TODO: filter based on query parameters, e.g.,
    # http://whatever.org/level/random?difficulty=hard
    level = random.choice(levels)
    return flask.Response(level[0], mimetype='text/plain')

@app.route('/level', methods=['POST'])
def add_entry():
    level = (request.form['id'],
             request.form['difficulty'],
             False)
    g.db.execute('INSERT INTO levels VALUES (?, ?, ?)', level)
    g.db.commit()
    return redirect(url_for('get_level', request.form['id']))

if __name__ == '__main__':
    arguments = docopt(__doc__)
    app.config['DEBUG'] = arguments['--debug']
    app.config['DATABASE'] = os.path.join(app.root_path, arguments['<filename>'])
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    app.run()
