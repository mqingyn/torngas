#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from torngas import webserver

PROJECT_OATH = os.path.dirname(os.path.abspath(__file__))
if __name__ == '__main__':
    server = webserver.Server()
    server.init(PROJECT_OATH, application=None)
    server.load_urls()
    server.load_application()
    server.server_start()

