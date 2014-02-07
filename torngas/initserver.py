#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
import logging, os, sys
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from tornado.log import enable_pretty_logging
from tornado.util import import_object
from torngas.utils import lazyimport
from torngas.exception import ConfigError

reload(sys)
sys.setdefaultencoding('utf-8')
application_module = lazyimport('torngas.application')
settings_module = lazyimport('torngas.helpers.settings_helper')
logger_module = lazyimport('torngas.helpers.logger_helper')

define("port", default=8000, help="run server on it", type=int)
define("setting", default='settings_devel', help="""config used to set the configuration file type,\n
settings_devel was default,you can set settings_functest or settings_production (it's your config file name)""",
       type=str)
define("address", default='localhost', help='listen host,default:localhost', type=str)
define("log_frefix", default='torngas', help='log file dirname', type=str)


class Server(object):
    def __init__(self, project_path=None, application=None):
        tornado.options.parse_command_line()
        self.application = application
        self.settings = settings_module.settings
        self.proj_path = project_path
        self.initializ()


    def initializ(self):
        pass


    def load_application(self, default_host='', transforms=None, wsgi=False, urls=None):
        #加载app，进行初始化配置,如无ap参数，则使用内置app初始化
        #加载本地化配置
        if self.settings.TRANSLATIONS:
            try:
                from tornado import locale

                locale.load_translations(self.settings.TRANSLATIONS_CONF.translations_dir)
            except:
                warnings.warn('locale dir load failure,maybe your config file is not set correctly.')

        if not self.application:
            self.application = application_module.AppApplication(handlers=urls or self.urls,
                                                                 default_host=default_host,
                                                                 transforms=transforms, wsgi=wsgi,
                                                                 **self.settings.TORNADO_CONF)

        self.application.project_path = self.proj_path \
            if self.proj_path.endswith('/') else self.proj_path + '/'

        tmpl = self.settings.TEMPLATE_CONFIG.template_engine
        self.application.tmpl = import_object(tmpl) if tmpl else None

        return self

    def load_urls(self):
        #加载app
        urls = []
        if self.settings.INSTALLED_APPS:
            for app in self.settings.INSTALLED_APPS:
                app_urls = import_object(app + '.urls.urls')
                urls.extend(app_urls)
        else:
            raise ConfigError('load urls error,INSTALLED_APPS not found!')
        self.urls = urls
        return self


    def server_start(self):

        logging.info('server starting...')
        logger_module.logger.load_config()
        #tornado把默认的根logger加了handler
        #把根logger的handler去除，然后重新绑定在tornado的logger下
        logging.getLogger().handlers = []
        enable_pretty_logging(None, logging.getLogger('tornado'))

        #服务启动

        from tornado.netutil import bind_sockets

        if self.settings.IPV4_ONLY:
            import socket

            sockets = bind_sockets(options.port, options.address, family=socket.AF_INET)
        else:
            sockets = bind_sockets(options.port, options.address)

        self.print_settings_info()
        http_server = tornado.httpserver.HTTPServer(self.application)
        http_server.add_sockets(sockets)
        logging.info('tornado server started. listen port: %s ,host address: %s' % (options.port, options.address))
        tornado.ioloop.IOLoop.instance().start()

    def print_settings_info(self):

        if self.settings.TORNADO_CONF.debug:
            logging.info('tornado version: %s' % tornado.version)
            logging.info('project path: %s' % self.proj_path)
            logging.info('setting file version: %s' % os.path.splitext(self.settings.settings_module.__file__)[0])
            logging.info('load middleware: %s' % list(self.settings.MIDDLEWARE_CLASSES).__str__())
            logging.info('debug open: %s' % self.settings.TORNADO_CONF.debug)
            logging.info('locale support: %s' % self.settings.TRANSLATIONS)
            logging.info('load subApp:\n %s' % self.settings.INSTALLED_APPS.__str__())
            logging.info('IPV4_Only: %s' % self.settings.IPV4_ONLY)
            logging.info('template engine: %s' % self.settings.TEMPLATE_CONFIG.template_engine)
            logging.info('log file path: %s' % logger_module.logger.get_log_abspath())





