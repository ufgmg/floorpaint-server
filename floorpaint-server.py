"""Usage: floorpaint-server.py [-ho <filename>] [--debug]

-h --help  show this
-o <filename>, --output <filename>  specify output file [default: ./grid.db]
--debug  use debug
"""
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort
from contextlib import closing
from docopt import docopt

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
def main_page(): pass
@app.route('/level')
def get_level():
    cur = g.db.execute('SELECT grid FROM entries WHERE id >= RAND() * (SELECT MAX(id) FROM entries) ORDER BY id LIMIT 1')
    entries = row[0] for row in cur.fetchone()
    return entries
@app.route('/level/add', methods=['POST'])
def add_entry():
    g.db.execute('insert into entries (grid) values (?)',
                 [request.form['grid']])
    g.db.commit()
    return redirect(url_for('main_page'))
if __name__ == '__main__':
    arguments = docopt(__doc__)
    app.config['DEBUG'] = arguments['--debug']
    app.config['DATABASE'] = os.path.join(app.root_path, arguments['<filename>'])
    if not os.path.isfile(app.config['DATABASE']):
        init_db()
    app.run()
