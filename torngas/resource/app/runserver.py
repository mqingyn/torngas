#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from torngas.initserver import Server

PROJECT_OATH = os.path.dirname(os.path.abspath(__file__))
if __name__ == '__main__':
    server = Server(PROJECT_OATH, application=None)
    server.load_urls().load_application().server_start()

