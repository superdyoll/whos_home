#!/usr/bin/env python3
from flask import Flask, g, render_template, request, redirect
import sqlite3
import pytz
from datetime import datetime

DATABASE = 'whos_home.db'
TIMEZONE = 'Europe/London'

app = Flask(__name__)


def unix_to_bst(timestamp):
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
SELECT t1.*, names.name
FROM history t1
    INNER JOIN (
        SELECT Max(unixdate), unixdate, mac, description
        FROM history
        GROUP BY mac
    ) t2
    ON t1.mac = t2.mac
    AND t1.unixdate = t2.unixdate
    LEFT JOIN names
        ON t1.mac = names.mac
""")

@app.route('/')
def index():
    devices = get_last_seens()

    # Convert row to a dict
    devices = [{
        'mac':d['mac'],
        'description':d['description'],
        'lastseen':unix_to_bst(d['unixdate']),
        'name': d['name'],
    } for d in devices]

    # Build the template variables
    unnamed_devices = filter(lambda x: x['name'] is None, devices)
    named_devices = filter(lambda x: x['name'] is not None, devices)

    return render_template('index.html',
                           devices=unnamed_devices,
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
    return redirect("/", code=302)


if __name__ == '__main__':
   app.run()
