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
from exception import ConfigError, ArgumentError, UrlError
from application import Application
from settings_manager import settings
from logger import SysLogger

reload(sys)
sys.setdefaultencoding('utf-8')


class Server(object):
    def __init__(self, ioloop=None):
        self.urls = []
        self.application = None
        self.httpserver = None
        self.ioloop = ioloop
        self.is_parselogger = False

    def _patch_httpserver(self):
        """
        重写httpserver的xheader配置，让gunicorn可以加载xheaders设置
        :return:
        """
        httpserver = sys.modules["tornado.httpserver"]
        try:
            xhs = settings.XHEADERS
        except:
            xhs = True

        class TorngasHTTPServer(httpserver.HTTPServer):
            def __init__(self, request_callback, xheaders=xhs, **kwargs):
                super(TorngasHTTPServer, self).__init__(request_callback,
                                                        xheaders=xheaders,
                                                        **kwargs)


        httpserver.HTTPServer = TorngasHTTPServer
        sys.modules["tornado.httpserver"] = httpserver

    def load_application(self, application=None):
        """

        :type application: torngas.application.Application subclass or instance
        :return:
        """
        self._patch_httpserver()
        if settings.TRANSLATIONS:
            try:
                from tornado import locale

                locale.load_translations(settings.TRANSLATIONS_CONF.translations_dir)
            except:
                warnings.warn('locale dir load failure,maybe your config file is not set correctly.')

        if not application:
            self._install_application(application)
        elif isinstance(application, Application):
            self.application = application
        elif issubclass(application, Application):
            self._install_application(application)
        else:
            raise ArgumentError('need torngas.application.Application instance object or subclass.')

        tmpl = settings.TEMPLATE_CONFIG.template_engine
        self.application.tmpl = import_object(tmpl) if tmpl else None

        return self.application

    def _install_application(self, application):
        if not self.urls:
            raise UrlError("urls not found.")
        if application:
            app_class = application
        else:
            app_class = Application

        tornado_conf = settings.TORNADO_CONF
        if 'default_handler_class' in tornado_conf and \
                isinstance(tornado_conf['default_handler_class'], basestring):
            tornado_conf['default_handler_class'] = import_object(tornado_conf['default_handler_class'])

        else:
            tornado_conf['default_handler_class'] = import_object('torngas.handler.ErrorHandler')

        tornado_conf['debug'] = settings.DEBUG
        self.application = app_class(handlers=self.urls,
                                     default_host='',
                                     transforms=None, wsgi=False,
                                     middlewares=settings.MIDDLEWARE_CLASSES,
                                     **tornado_conf)

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

    def load_httpserver(self, sockets=None, **kwargs):
        if not sockets:
            from tornado.netutil import bind_sockets

            if settings.IPV4_ONLY:
                import socket

                sockets = bind_sockets(options.port, options.address, family=socket.AF_INET)
            else:
                sockets = bind_sockets(options.port, options.address)

        http_server = tornado.httpserver.HTTPServer(self.application, **kwargs)

        http_server.add_sockets(sockets)
        self.httpserver = http_server
        return self.httpserver

    def server_start(self, sockets=None, **kwargs):
        if not self.httpserver:
            self.load_httpserver(sockets, **kwargs)

        self.start()

    def load_all(self, application=None, sockets=None, **kwargs):
        self.parse_command()
        self.load_urls()
        self.load_application(application)
        if not self.httpserver:
            self.load_httpserver(sockets, **kwargs)

    def start(self):
        if not self.is_parselogger:
            self.parse_logger()

        self.print_settings_info()

        if not self.ioloop:
            self.ioloop = tornado.ioloop.IOLoop.instance()

        self.ioloop.start()

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

    def parse_command(self, args=None, final=True):
        """
        解析命令行参数，解析logger配置
        :return:
        """
        self.define()
        parse_command_line(args, final)
        self.parse_logger()

    def define(self):
        """
        定义命令行参数,你可以自定义很多自己的命令行参数，或重写此方法覆盖默认参数
        :return:
        """
        define("port", default=8000, help="run server on it", type=int)
        define("settings", help="setting module name", type=str)
        define("address", default='0.0.0.0', help='listen host,default:0.0.0.0', type=str)

    def parse_logger(self):
        """
        加载logger配置，如果使用gunicorn，你需要手动调用加载
        :return:
        """
        SysLogger.parse_logger()
        self.is_parselogger = True


def run(application=None, sockets=None, **kwargs):
    server = Server()
    server.load_all(application, sockets, **kwargs)
    server.start()