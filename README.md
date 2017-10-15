# whos_home

A series of scripts to automate checking who is home

# Installation

Install the required packages:
```bash
# Global packages
sudo apt-get install nmap
sudo pip install virtualenv

# Python packages
virtualenv create venv
source venv/bin/activate
pip install Flask
pip install pytz
pip install sqlite3
```

set up a CRON job to run `sudo ./whos_home.sh | python parse_whos_home_output.py` every 5 minutes or so.

start the flask server with `python -m flask run`
