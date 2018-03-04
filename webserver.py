#!/usr/bin/env python3
from flask import Flask, g, render_template, request, redirect
import sqlite3
import pytz
from datetime import datetime, timedelta
import calendar

from common import mac_int_to_str, mac_str_to_int

DATABASE = 'whos_home.db'
TIMEZONE = 'Europe/London'
CITY = 'Southampton'
COUNTRY = 'United Kingdom'

# Domain running an instance of harmony-api (blank for disable)
# in the format of: "http://127.0.0.1:8282/"
HARMONY_DOMAIN = ""


# convert it to tz
tz = pytz.timezone(TIMEZONE)

app = Flask(__name__)


def pretty_date(diff):
    """
    get a date difference and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    second_diff = int(round(diff.total_seconds()))
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 60:
            return "just now"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(round(second_diff / 60))) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(round(second_diff / 3600))) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(int(round(day_diff))) + " days ago"
    if day_diff < 31:
        return str(int(round(day_diff / 7))) + " weeks ago"
    if day_diff < 365:
        return str(int(round(day_diff / 30))) + " months ago"
    return str(int(round(day_diff / 365))) + " years ago"


def unix_to_bst(timestamp):
    # get time in UTC
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
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
    LEFT JOIN names
        ON t1.mac = names.mac
""")

def get_last_note():
    return get_db().execute("""
    SELECT note, unixdate
    FROM notes 
    WHERE id = 1
    """)


STATUS_IN = "in"
STATUS_JUST_LEFT = "just-left"
STATUS_OUT = "out"


def get_diff_from_now(uk_time):
    utc_dt = datetime.now(pytz.utc)  # UTC time
    dt = utc_dt.astimezone(tz)  # local time
    return dt - uk_time


def determine_color(uk_time):
    diff_time = get_diff_from_now(uk_time)
    if diff_time < timedelta(minutes=10):
        return STATUS_IN
    elif diff_time < timedelta(minutes=60):
        return STATUS_JUST_LEFT
    else:
        return STATUS_OUT


@app.route('/')
def index():
    devices = get_last_seens()
    # Convert row to a dict
    devices = [{
        'mac': mac_int_to_str(d['mac']),
        'description': d['description'],
        'lastseen': unix_to_bst(d['unixdate']).strftime("%d/%m %H:%M"),
        'pretty_lastseen': pretty_date(
            get_diff_from_now(unix_to_bst(d['unixdate']))),
        'color': determine_color(unix_to_bst(d['unixdate'])),
        'name': d['name'],
    } for d in devices]
    devices.reverse()

    # Build the template variables
    unnamed_devices = filter(lambda x: x['name'] is None, devices)
    named_devices = filter(lambda x: x['name'] is not None, devices)
    
    notes = get_last_note()
    notes = [{
        'note': d['note'],
        'pretty_date': pretty_date( get_diff_from_now( unix_to_bst(d['unixdate']))),
    } for d in notes]

    return render_template('index.html',
                           devices=unnamed_devices,
                           named_devices=named_devices,
                           harmony_domain=HARMONY_DOMAIN,
                           city=CITY,
                           country=COUNTRY,
                           note=notes[0])


def add_device_name(mac, name):
    get_db().execute(
        """INSERT OR REPLACE INTO names (mac, name) VALUES (?,?)""",
        [mac, name]
    )


def remove_device_name(name):
    get_db().execute(
        """DELETE FROM names WHERE name=(?)""",
        [name]
    )
    
def add_note_to_db(note):
    d = datetime.utcnow()
    unixtime = calendar.timegm(d.utctimetuple())
    get_db().execute(
        """INSERT OR REPLACE INTO notes (id, note, unixdate) VALUES(1, ?, ?)""",
        [note,unixtime]
    )
    

@app.route('/edit_note', methods=['POST'])   
def edit_note():
    note = request.form['note']
    add_note_to_db(note)
    get_db().commit()
    return redirect("/", code=302)
    

@app.route('/name_device', methods=['POST'])
def name_device():
    mac = mac_str_to_int(request.form['mac'])
    name = request.form['name']
    add_device_name(mac, name)
    get_db().commit()
    return redirect("/", code=302)


@app.route('/remove_device', methods=['POST'])
def remove_device():
    name = request.form['name']
    remove_device_name(name)
    get_db().commit()
    return redirect("/", code=302)


if __name__ == '__main__':
    app.run()
