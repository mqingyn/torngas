#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from torngas.webserver import Server

PROJECT_OATH = os.path.dirname(os.path.abspath(__file__))
if __name__ == '__main__':
    os.environ.setdefault("SETTINGS_MODULE", "settings.setting")
    Server().runserver(PROJECT_OATH)

