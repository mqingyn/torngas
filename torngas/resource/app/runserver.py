#!/usr/local/bin/python
#coding=utf-8
import os
from torngas.initserver import Server

PROJECT_NAME = "app"
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("TORNGAS_ONLINE_SETTINGS_MODULE", "%s.settings_production" % PROJECT_NAME)
os.environ.setdefault("TORNGAS_DEV_SETTINGS_MODULE", "%s.settings_devel" % PROJECT_NAME)
os.environ.setdefault("TORNGAS_TEST_SETTINGS_MODULE", "%s.settings_functest" % PROJECT_NAME)
if __name__ == '__main__':
    server = Server(PROJECT_PATH, application=None)
    server.load_urls()
    server.load_application()
    server.server_start()

