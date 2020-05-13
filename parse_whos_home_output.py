#!/usr/bin/env python3
import time
import argparse
import sys
import re
import os.path
import sqlite3

from common import mac_str_to_int

hex_r = r'[A-Z0-9]'
MAC_ADDRESS_REGEX = re.compile(
    "{0}{0}:{0}{0}:{0}{0}:{0}{0}:{0}{0}:{0}{0}".format(hex_r))

DEVICE_INFO_REGEX = re.compile(r"\((.*)\)$")


def create_db(conn):
    c = conn.cursor()

    # Create history table
    c.execute('''
CREATE TABLE IF NOT EXISTS history(
    mac UNSIGNED INTEGER PRIMARY KEY,
    unixdate UNSIGNED INTEGER,
    description TEXT
)''')
    # Create names table
    c.execute('''
CREATE TABLE IF NOT EXISTS names(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mac INTEGER NOT NULL,
    name TEXT NOT NULL
)''')
    # Create notes table
    c.execute('''
CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note TEXT NOT NULL,
    unixdate UNSIGNED INTEGER
)''')

    # Save (commit) the changes
    conn.commit()


def delete_db(conn):
    c = conn.cursor()
    c.execute('''DROP TABLE history''')
    c.execute('''DROP TABLE names''')
    c.execute('''DROP TABLE notes''')
    conn.commit()


def insert_data(
        conn,
        unixtime,
        all_data,
):
    c = conn.cursor()
    c.executemany(
        'INSERT OR REPLACE INTO history (mac, unixdate, description) VALUES (?,?,?)',
        [(d[0], unixtime, d[1]) for d in all_data]
    )


def cleanup_data(data):
    data = [l for l in data if "MAC Address:" in l]
    for line in data:
        mac = mac_str_to_int(MAC_ADDRESS_REGEX.search(line).group(0))
        info = DEVICE_INFO_REGEX.search(line).group(1)
        yield mac, info


def main(db_name, should_create_db, migrate):
    exists = os.path.isfile(db_name)
    with sqlite3.connect(db_name) as conn:
        # Init the DB
        if not exists:
            create_db(conn)
            print("Database file '{}' didn't exist, created.".format(db_name))
        elif should_create_db:
            delete_db(conn)
            create_db(conn)
            print("Deleted database and recreated.")
        elif migrate:
            create_db(conn)
            print("Migrated database successfully")

        # Parse stdin
        data = sys.stdin.read().splitlines()

        now = int(time.time())
        all_data = cleanup_data(data)
        insert_data(conn, now, all_data)
        conn.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create_db", action='store_true')
    parser.add_argument("--database", "-d", default="whos_home.db")
    parser.add_argument("--migrate", "-m", default=False)
    args = parser.parse_args()
    main(args.database, args.create_db, args.migrate)
