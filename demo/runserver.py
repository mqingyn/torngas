#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from tornado.options import options, parse_command_line
from torngas.webserver import Server

if __name__ == '__main__':

    parse_command_line()
    setting = options.settings
    if not setting:
        os.environ.setdefault('TORNGAS_APP_SETTINGS', 'settings.setting')

    if options.servermode == 'httpserver':


        server = Server()
        server.runserver()

    elif options.servermode == 'logserver':
        from torngas.logger.server import run_logserver

        run_logserver()
    else:
        print 'wrong servermode,please run python main.py --help'