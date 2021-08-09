#! /usr/bin/env python3

import os
import csv
import json
import urllib
import urllib.request
import sqlite3


def get_example(q):
    url = 'https://api.dictionaryapi.dev/api/v2/entries/en_US/' + \
        urllib.parse.quote_plus(q)
    try:
        with urllib.request.urlopen(url) as resp:
            s = resp.read()
            r = json.loads(s)
            if isinstance(r, list):
                example = r[0]['meanings'][0]['definitions'][0]['example']
                return example
    except Exception as e:
        pass
    return ''


def filter_csv_dict(input, output, level):
    '''
    从ecdict.csv过滤指定级别的单词
    level:
        zk = 中考
        gk = 高考
        cet4 = 四级
        oxford = 牛津三千核心词汇
    '''
    def _matches(oxford, tag):
        if level == 'oxford':
            return oxford == '1'
        return level in tag

    print(f'filter {level} from {input} to {output}...')
    with open(input, newline='', encoding='utf-8') as fin:
        reader = csv.reader(fin)
        con = sqlite3.connect(output + '.db')
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXISTS words')
        cur.execute(
            '''
            CREATE TABLE words (
                name TEXT NOT NULL PRIMARY KEY,
                phonetic TEXT NOT NULL,
                definition TEXT NOT NULL,
                translation TEXT NOT NULL,
                collins TEXT NOT NULL,
                exchange TEXT NOT NULL,
                examples TEXT NOT NULL,
                corrects INTEGER NOT NULL,
                errors INTEGER NOT NULL
            )''')
        con.commit()
        with open(output + '.csv', 'w', encoding='utf-8') as fout:
            writer = csv.writer(fout)
            count = 0
            for row in reader:
                oxford = row[6].strip()
                tag = row[7]
                if _matches(oxford, tag):
                    ex = get_example(row[0])
                    print(f'{row[0]} -> {ex}')
                    # name, phonetic, definition, translation, collins, exchange, examples:
                    it = [row[0], row[1], row[2], row[3], row[5], row[10], ex]
                    writer.writerow(it)
                    it.append(0)
                    it.append(0)
                    cur.execute(
                        'INSERT INTO words VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', it)
                    count = count + 1
            print(f'{count} words wrote.')
        cur.close()
        con.commit()


if __name__ == '__main__':
    f = os.path.abspath(__file__)
    p = os.path.dirname(f)
    pp = os.path.dirname(p)
    input = os.path.join(pp, 'ECDICT', 'ecdict.csv')
    output = os.path.join(p, 'ecdict')
    filter_csv_dict(input, output, 'zk')
