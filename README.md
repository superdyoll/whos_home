# whos_home

A series of scripts to automate checking who is home

# Installation

Install the required packages:
```bash
# Global packages
sudo apt-get install nmap
sudo pip install virtualenv

# Python packages
virtualenv venv
source venv/bin/activate
pip install Flask pytz
```

Edit the root crontab (nmap requires to be run with root permission to get mac addresses) and add:
```bash
*/5 * * * * /home/<username>/whos_home.sh | /home/<username>/whos_home/parse_whos_home_output.py
```
To update the database every 5 minutes, If you have a faster processor you could do it every minute. Make sure the full paths to the scripts are correct.

Start the flask server with `export FLASK_APP=webserver.py; python -m flask run`

# Magic Mirror Module
Also included in this repository is a Magic Mirror module. To include it in your mirror add this repository to the modules of your mirror and then include it as normal.

When you want to add new devices you'll need to run up the flask server and connect via a web browser to but once the devices are added as long as the cron job is running they will be updated.
