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
from settings_manager import settings

reload(sys)
sys.setdefaultencoding('utf-8')
define("port", default=8000, help="run server on it", type=int)
define("settings", help="setting module name", type=str)
define("address", default='0.0.0.0', help='listen host,default:0.0.0.0', type=str)


class Server(object):
    def __init__(self):
        self.urls = []
        self.application = None

    def load_application(self, application=None):

        if settings.TRANSLATIONS:
            try:
                from tornado import locale

                locale.load_translations(settings.TRANSLATIONS_CONF.translations_dir)
            except:
                warnings.warn('locale dir load failure,maybe your config file is not set correctly.')

        if not application:
            if not self.urls:
                raise BaseError("urls not found.")
            from torngas.application import Application

            tornado_conf = settings.TORNADO_CONF
            tornado_conf['debug'] = settings.DEBUG
            self.application = Application(handlers=self.urls,
                                           default_host='',
                                           transforms=None, wsgi=False,
                                           middlewares=settings.MIDDLEWARE_CLASSES,
                                           **tornado_conf)
        else:
            self.application = application

        tmpl = settings.TEMPLATE_CONFIG.template_engine
        self.application.tmpl = import_object(tmpl) if tmpl else None

        return self.application

    def load_urls(self):
        urls = []
        if settings.INSTALLED_APPS:
            for app_name in settings.INSTALLED_APPS:
                app_urls = import_object(app_name + '.urls.urls')
                urls.extend(app_urls)
        else:
            raise ConfigError('load urls error,INSTALLED_APPS not found!')
        self.urls = urls
        return self.urls

    def server_start(self, sockets=None, **kwargs):

        if not sockets:
            from tornado.netutil import bind_sockets

            if settings.IPV4_ONLY:
                import socket

                sockets = bind_sockets(options.port, options.address, family=socket.AF_INET)
            else:
                sockets = bind_sockets(options.port, options.address)
        try:
            xheaders = settings.XHEADERS
        except:
            xheaders = True

        http_server = tornado.httpserver.HTTPServer(self.application, xheaders=xheaders, **kwargs)

        http_server.add_sockets(sockets)
        self.print_settings_info()

        tornado.ioloop.IOLoop.instance().start()

    def print_settings_info(self):

        if settings.DEBUG:
            print 'tornado version: %s' % tornado.version
            print 'load middleware:'
            for middl in settings.MIDDLEWARE_CLASSES:
                print ' -', str(middl)
            print 'locale support: %s' % settings.TRANSLATIONS
            print 'load apps:'
            for app in settings.INSTALLED_APPS:
                print ' -', str(app)
            print 'IPV4_Only: %s' % settings.IPV4_ONLY
            print 'template engine: %s' % settings.TEMPLATE_CONFIG.template_engine
            print 'server started. development server at http://%s:%s/' % (options.address, options.port)

    def parse_command(self):
        parse_command_line()


def run(application=None, sockets=None, **kwargs):
    server = Server()
    server.parse_command()
    server.load_urls()
    server.load_application(application)
    server.server_start(sockets=None, **kwargs)
