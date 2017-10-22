#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from webserver import app

if __name__ == '__main__':
    WSGIServer(app).run()

fastcgi.server = ("/" =>
    ((
        "socket" => "/tmp/whos_home-fcgi.sock",
        "bin-path" => "/home/www/whos_home.fcgi",
        "check-local" => "disable",
        "max-procs" => 1
    ))
)

alias.url = (
    "/static/" => "/home/www/whos_home/static"
)

url.rewrite-once = (
    "^(/static($|/.*))$" => "$1",
    "^(/.*)$" => "/whos_home.fcgi$1"
)

