#!/usr/bin/env python3
from typing import List, Tuple
import time
import argparse
import sys
import re
import os.path
import sqlite3

hex_r = r'[A-Z0-9]'
MAC_ADDRESS_REGEX = re.compile("{0}{0}:{0}{0}:{0}{0}:{0}{0}:{0}{0}:{0}{0}".format(hex_r))

DEVICE_INFO_REGEX = re.compile(r"\((.*)\)$")

def create_db(conn : sqlite3.Connection):
    c = conn.cursor()

    # Create history table
    c.execute('''
CREATE TABLE history(
    unixdate UNSIGNED INTEGER,
    mac TEXT,
    description TEXT
)''')

    # Create logs table
    c.execute('''
CREATE TABLE logs(
    unixdate UNSIGNED INTEGER,
    error TEXT
)''')

    # Save (commit) the changes
    conn.commit()

def delete_db(conn : sqlite3.Connection):
    c = conn.cursor()
    c.execute('''DROP TABLE logs''')
    c.execute('''DROP TABLE history''')
    conn.commit()

def insert_data(
    conn : sqlite3.Connection,
    unixtime : int,
    all_data : Tuple[str,str],
    ):
        c = conn.cursor()
        c.executemany(
            'INSERT INTO history VALUES (?,?,?)',
            [(unixtime, d[0], d[1]) for d in all_data]
        )

def cleanup_data(data:List[str]):
    data = [l for l in data if "MAC Address:" in l]
    for line in data:
        mac = MAC_ADDRESS_REGEX.search(line).group(0)
        info = DEVICE_INFO_REGEX.search(line).group(1)
        yield mac, info

def main(db_name : str, should_create_db : bool):
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

        # Parse stdin
        data = sys.stdin.read().splitlines()

        now = int(time.time())
        all_data = cleanup_data(data)
        insert_data(conn, now, all_data)
        conn.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create_db", action='store_true')
    parser.add_argument("--database","-d", default="whos_home.db")
    args = parser.parse_args()
    main(args.database, args.create_db)
