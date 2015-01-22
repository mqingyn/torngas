#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from tornado.options import define, options
from torngas.webserver import Server

define("runmode", default='runserver', help='run mode, runserver|syncdb', type=str)

os.environ.setdefault('TORNGAS_APP_SETTINGS', 'settings.setting')

if __name__ == '__main__':
    """
     If you want to quickly start the service , you can do like this:
     from torngas.webserver import run

     run()
    """

    server = Server()
    server.parse_command()

    if options.runmode == 'syncdb':
        from helloworld.sync_db import syncdb

        syncdb()
    elif options.runmode == 'runserver':
        server.load_urls()
        server.load_application()
        server.load_httpserver()
        server.server_start()
    else:
        exit(0)
