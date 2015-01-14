#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
import sys
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options, parse_command_line
from tornado.util import import_object
from torngas.exception import ConfigError, BaseError

reload(sys)
sys.setdefaultencoding('utf-8')

define("port", default=8000, help="run server on it", type=int)
define("settings", help="setting module name", type=str)
define("address", default='127.0.0.1', help='listen host,default:127.0.0.1', type=str)
parse_command_line()
# 一些配置的使用必须先parse_command_line()
from settings_manager import settings
from logger import SysLogger

class Server(object):
    settings = settings
    urls = []
    application = None

    def load_application(self, application=None):

        if self.settings.TRANSLATIONS:
            try:
                from tornado import locale

                locale.load_translations(self.settings.TRANSLATIONS_CONF.translations_dir)
            except:
                warnings.warn('locale dir load failure,maybe your config file is not set correctly.')

        if not application:
            if not self.urls:
                raise BaseError("urls not found.")
            from torngas.application import Application

            self.application = Application(handlers=self.urls,
                                           default_host='',
                                           transforms=None, wsgi=False,
                                           **self.settings.TORNADO_CONF)
        else:
            self.application = application

        tmpl = self.settings.TEMPLATE_CONFIG.template_engine
        self.application.tmpl = import_object(tmpl) if tmpl else None

        return self

    def load_urls(self):
        urls = []
        if self.settings.INSTALLED_APPS:
            for app_name in self.settings.INSTALLED_APPS:
                app_urls = import_object(app_name + '.urls.urls')
                urls.extend(app_urls)
        else:
            raise ConfigError('load urls error,INSTALLED_APPS not found!')
        self.urls = urls
        return self

    def server_start(self, sockets=None, **kwargs):

        if not sockets:
            from tornado.netutil import bind_sockets

            if self.settings.IPV4_ONLY:
                import socket

                sockets = bind_sockets(options.port, options.address, family=socket.AF_INET)
            else:
                sockets = bind_sockets(options.port, options.address)

        http_server = tornado.httpserver.HTTPServer(self.application, **kwargs)

        http_server.add_sockets(sockets)
        self.print_settings_info()

        tornado.ioloop.IOLoop.instance().start()

    def print_settings_info(self):

        if self.settings.TORNADO_CONF.debug:
            print 'tornado version: %s' % tornado.version
            print 'load middleware:'
            for middl in self.settings.MIDDLEWARE_CLASSES:
                print ' -', str(middl)
            print 'debug open: %s' % self.settings.TORNADO_CONF.debug
            print 'locale support: %s' % self.settings.TRANSLATIONS
            print 'load apps:'
            for app in self.settings.INSTALLED_APPS:
                print ' -', str(app)
            print 'IPV4_Only: %s' % self.settings.IPV4_ONLY
            print 'template engine: %s' % self.settings.TEMPLATE_CONFIG.template_engine
            print 'server started. development server at http://%s:%s/' % (options.address, options.port)


def run(application=None, sockets=None, **kwargs):
    server = Server()
    server.load_urls()
    server.load_application(application)
    server.server_start(sockets=None, **kwargs)


