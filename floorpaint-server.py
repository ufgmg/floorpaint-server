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
from flask import Response
from flask import request
from flask import send_file
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

@app.route('/success')
def success():
    return "Success!"

@app.route('/level/random')
def get_random_level():
    # http://whatever.org/level/random?difficulty=hard
    difficulty = request.args.get('difficulty')
    if difficulty is not None:
        query = "SELECT * FROM levels WHERE difficulty='" + difficulty + "'"
    else:
        query = 'SELECT * FROM levels'
    cur = g.db.execute(query)
    levels = cur.fetchall()
    level = random.choice(levels)
    return Response(level[0], mimetype='text/plain')

@app.route('/level/new')
def new_level():
    return send_file(open(os.path.join(app.root_path, 'static/new.html'), 'rb'),
                     mimetype='text/html')

@app.route('/level', methods=['POST'])
def post_level():
    level = (request.form['id'],
             request.form['difficulty'],
             True)
    g.db.execute('INSERT INTO levels VALUES (?, ?, ?)', level)
    g.db.commit()
    return redirect(url_for('success'))

if __name__ == '__main__':
    args = docopt(__doc__)
    app.config['DEBUG'] = args['--debug']
    app.config['DATABASE'] = os.path.join(app.root_path,
                                          args['DATABASE_FILE'])
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    app.run()
