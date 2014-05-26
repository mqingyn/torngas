#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
import logging, os, sys
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from tornado.util import import_object
from torngas.utils import lazyimport
from torngas.exception import ConfigError, BaseError

reload(sys)
sys.setdefaultencoding('utf-8')
define("port", default=8000, help="run server on it", type=int)
define("setting", default='setting', help="""config used to set the configuration file type,\n
settings_devel was default,you can set settings_functest or settings_production (it's your config file name)""",
       type=str)
define("address", default='127.0.0.1', help='listen host,default:127.0.0.1', type=str)
define("server", default='runserver', help="run server mode", type=str)


class Server(object):
    settings = None
    urls = []
    application = None

    def parse_command_line(self):
        tornado.options.parse_command_line()
        from torngas.settings_manager import settings
        self.settings = settings
        return self

    def load_application(self, application=None):
        #加载app，进行初始化配置,如无ap参数，则使用内置app初始化
        #加载本地化配置
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
            self.application = application(handlers=self.urls,
                                           default_host='',
                                           transforms=None, wsgi=False,
                                           **self.settings.TORNADO_CONF)

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

    def server_start(self, no_keep_alive=False, io_loop=None,
                     xheaders=False, ssl_options=None, protocol=None, sockets=None, **kwargs):

        if not sockets:
            from tornado.netutil import bind_sockets

            if self.settings.IPV4_ONLY:
                import socket

                sockets = bind_sockets(options.port, options.address, family=socket.AF_INET)
            else:
                sockets = bind_sockets(options.port, options.address)

        http_server = tornado.httpserver.HTTPServer(self.application, no_keep_alive, io_loop,
                                                    xheaders, ssl_options, protocol, **kwargs)
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
            print 'server started. development server at http://%s:%s/' % (options.addr, options.port)

    def runserver(self, application=None):
        self.init()
        self.load_urls()
        self.load_application(application)
        self.server_start()


