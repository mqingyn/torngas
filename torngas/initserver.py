#!/usr/local/bin/python
#coding=utf-8
import os
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from tornado.log import enable_pretty_logging
from tornado.util import import_object
from torngas.utils import lazyimport
from torngas.exception import ConfigError


application_module = lazyimport('torngas.application')
settings_module = lazyimport('torngas.helpers.settings_helper')
logger_module = lazyimport('torngas.helpers.logger_helper')

define("port", default=8000, help="run server on it", type=int)
define("config", default='devel', help="if run as online ,use online,settings type:online, test, dev", type=str)
define("address", default='localhost', help='listen host,default:localhost', type=str)


class Server(object):
    def __init__(self, project_path=None, settings=settings_module.settings, application=None):
        self.application = application
        self.settings = settings
        self.proj_path = project_path
        self.urls = []

    def load_application(self):
        #加载app，进行初始化配置,如无ap参数，则使用内置app初始化
        logger_module.logger.load_config()
        tornado.options.parse_command_line()
        #tornado把默认的根logger加了handler
        #把根logger的handler去除，然后重新绑定在tornado的logger下
        logging.getLogger().handlers = []
        enable_pretty_logging(None, logging.getLogger('tornado'))
        #加载本地化配置
        tornado.locale.load_translations(self.settings.TRANSLATIONS_CONF.translations_dir)
        #初始化app
        if not self.application:
            self.application = application_module.AppApplication(handlers=self.urls,
                                                                 settings=self.settings.TORNADO_CONF)

        self.application.project_path = self.proj_path if self.proj_path.endswith('/') else self.proj_path + '/'
        self.application.tmpl = import_object(self.settings.TEMPLATE_ENGINE) if self.settings.TEMPLATE_ENGINE else None
        return self.application

    def load_urls(self):
        #加载app

        if self.settings.INSTALLED_APPS:
            for app in self.settings.INSTALLED_APPS:
                app_urls = import_object(app + '.urls.urls')
                self.urls.extend(app_urls)

        else:
            raise ConfigError('load urls error,INSTALLED_APPS not found!')

        return self.urls


    def server_start(self):
        #服务启动
        if self.settings.IPV4_ONLY:
            import socket
            from tornado.netutil import bind_sockets

            sockets = bind_sockets(options.port, options.address, family=socket.AF_INET)
        else:
            sockets = bind_sockets(options.port, options.address)

        self.print_settings_info()
        http_server = tornado.httpserver.HTTPServer(self.application)
        http_server.add_sockets(sockets)
        tornado.ioloop.IOLoop.instance().start()
        print 'tornado server started. listen port: %s ,host address: %s' % (options.port, options.address)

    def print_settings_info(self):

        print 'tornado version: %s' % tornado.version
        print 'project path: %s' % self.proj_path
        print 'load middleware: %s' % list(self.settings.MIDDLEWARE_CLASSES).__str__()
        print 'debug open: %s' % self.settings.TORNADO_CONF.debug
        print 'load subApp:\n %s' % self.settings.INSTALLED_APPS.__str__()
        print 'IPV4_Only: %s' % self.settings.IPV4_ONLY
        print 'template engine: %s' % self.settings.TEMPLATE_ENGINE





