#!/usr/bin/env python
# -*- coding: utf-8 -*-
from torngas.webserver import Server
# import os

"""
run at gunicorn.
gunicorn -c gunicorn.py.conf run_gunicorn:app
torngas settings 写在gunicorn.conf.py中：
os.environ.setdefault('TORNGAS_APP_SETTINGS', 'settings.setting')
"""

server = Server()
server.parse_command()
server.load_urls()

app = server.load_application()


