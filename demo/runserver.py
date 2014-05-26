#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from torngas.webserver import Server
from tornado.options import options

PROJ_PATH = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    server = Server(PROJ_PATH)
    server.parse_command_line()

    setting = options.settings
    if not setting:
        os.environ.setdefault('TORNGAS_APP_SETTINGS', 'settings.setting')

    if options.servermode == 'httpserver':
        server.runserver()

    elif options.servermode == 'logserver':
        from torngas.logger.server import run_logserver

        run_logserver()
    else:
        print 'wrong servermode,please run python main.py --help'