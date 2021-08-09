#! /usr/bin/env python3

import os
import json
import random
import urllib.request
import sqlite3
from collections import namedtuple
from flask import Flask, request, render_template

Word = namedtuple('Word', ['name', 'phonetic', 'definition',
                  'translation', 'collins', 'exchange', 'examples', 'corrects', 'errors'])


def open_db():
    return sqlite3.connect(os.path.join(os.path.dirname(__file__), 'ecdict.db'))


def load_words(max_words=50):
    with open_db() as con:
        words = []
        cur = con.cursor()
        for row in cur.execute('SELECT name, phonetic, definition, translation, collins, exchange, examples, corrects, errors FROM words'):
            words.append(Word(*row))
        cur.close()
        # find errors >= corrects:
        selected = [word for word in words if word.errors >= word.corrects]
        if len(selected) >= max_words:
            random.shuffle(selected)
            selected = selected[:max_words]
        else:
            # find corrects > erros:
            less_corrects = sorted([word for word in words if word.corrects >
                                    word.errors], key=lambda w: w.corrects - w.errors)
            left = max_words - len(selected)
            selected.extend(less_corrects[:left])
            random.shuffle(selected)
        return [{
            'name': word[0],
            'phonetic': word[1],
            'definition': word[2],
            'translation': word[3],
            'collins': word[4],
            'exchange': word[5],
            'examples': word[6],
            'corrects': word[7],
            'errors': word[8]
        } for word in selected]


# init web app:
app = Flask(__name__)


@app.route('/')
def index():
    words = load_words()
    print(f'loaded {len(words)} words.')
    model = dict(words=json.dumps(words))
    return render_template('index.html', **model)


@app.route('/results', methods=['POST'])
def results():
    rs = request.json
    with open_db() as con:
        cur = con.cursor()
        for r in rs:
            params = (r['errors'], r['corrects'], r['name'])
            cur.execute(
                'UPDATE words SET errors=?, corrects=? WHERE name=?', params)
        cur.close()
        con.commit()
    return dict(udated=len(rs))


@app.route('/reset', methods=['POST'])
def reset():
    with open_db() as con:
        cur = con.cursor()
        cur.execute('UPDATE words SET errors=?, corrects=?', (0, 0))
        cur.close()
        con.commit()
    return dict()
