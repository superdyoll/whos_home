#!/usr/bin/env python3
from flask import Flask, g, render_template, request
import sqlite3
import pytz
from datetime import datetime

DATABASE = 'whos_home.db'
TIMEZONE = 'Europe/London'

app = Flask(__name__)


def unix_to_bst(timestamp : int):
    # get time in UTC
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    # convert it to tz
    tz = pytz.timezone(TIMEZONE)
    return utc_dt.astimezone(tz)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_last_seens():
    return get_db().execute("""
SELECT t1.*
FROM history t1
    LEFT JOIN history t2
        ON t1.mac = t2.mac
        AND t1.unixdate < t2.unixdate
    LEFT JOIN names 
        ON t1.mac = names.mac
WHERE t2.unixdate IS NULL and names.mac IS NULL
""")

def get_named_last_seens():
    return get_db().execute("""
SELECT t1.*, names.name
FROM history t1
    LEFT JOIN history t2
        ON t1.mac = t2.mac 
        AND t1.unixdate < t2.unixdate
    JOIN names
        ON t1.mac = names.mac
WHERE t2.unixdate IS NULL
""")

@app.route('/')
def index():
    devices = [(e['mac'], unix_to_bst(e['unixdate']),e['description']) for e in get_last_seens()]
    named_devices = [
        (
            e['mac'],
            e['name'],
            unix_to_bst(e['unixdate']),
            e['description']
         ) for e in get_named_last_seens()]
    return render_template('index.html',
                           devices=devices,
                           named_devices=named_devices)
def add_device_name(mac,name):
    get_db().execute(
        """INSERT OR REPLACE INTO names (mac, name) VALUES (?,?)""",
        [mac, name]
    )

@app.route('/name_device', methods=['POST'])
def name_device():
    mac = request.form['mac']
    name = request.form['name']
    add_device_name(mac, name)
    get_db().commit()
    return "<p>Successfully added</p>"
