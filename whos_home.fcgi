#!/home/www/whos_home/venv/bin/python
from flup.server.fcgi import WSGIServer
from webserver import app
from werkzeug.contrib.fixers import LighttpdCGIRootFix


if __name__ == '__main__':
    WSGIServer(LighttpdCGIRootFix(app)).run()
