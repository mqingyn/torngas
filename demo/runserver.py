#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

os.environ.setdefault('TORNGAS_APP_SETTINGS', 'settings.setting')

if __name__ == '__main__':
    from torngas.webserver import run
    run()


