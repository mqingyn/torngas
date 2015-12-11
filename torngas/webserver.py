#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
import logging
import sys, os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import options, parse_command_line, add_parse_callback, OptionParser
from tornado.log import define_logging_options, LogFormatter
from tornado.util import import_object
from exception import ConfigError, ArgumentError, UrlError
from application import Application
from settings_manager import settings
from logger import enable_pretty_logging, ProcessLogTimedFileHandler

reload(sys)
sys.setdefaultencoding('utf-8')


class Server(object):
    def __init__(self, ioloop=None):
        self.urls = []
        self.application = None
        self.httpserver = None
        self.ioloop = ioloop

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
        self.print_settings_info()

        if not self.ioloop:
            self.ioloop = tornado.ioloop.IOLoop.instance()

        self.ioloop.start()

    def print_settings_info(self):
        if settings.DEBUG:
            print('tornado version: %s' % tornado.version)
            print('locale support: %s' % settings.TRANSLATIONS)
            print('load apps:')
            for app in settings.INSTALLED_APPS:
                print(' - %s' % str(app))
            print('template engine: %s' % (settings.TEMPLATE_CONFIG.template_engine or 'default'))
            print('server started. development server at http://%s:%s/' % (options.address, options.port))

    def parse_command(self, args=None, final=False):
        """
        解析命令行参数，解析logger配置
        :return:
        """
        self.define()
        add_parse_callback(self.parse_logger_callback)
        parse_command_line(args, final)
        options.run_parse_callbacks()

    def parse_logger_callback(self):
        if options.disable_log:
            options.logging = None
        if options.log_file_prefix and options.log_port_prefix:
            options.log_file_prefix += ".%s" % options.port
        if options.log_patch:
            logging.handlers.TimedRotatingFileHandler = ProcessLogTimedFileHandler
        tornado_logger = logging.getLogger('tornado')
        enable_pretty_logging(logger=tornado_logger)
        logdir = options.logging_dir or settings.LOGGING_DIR
        for log in settings.LOGGING:
            opt = OptionParser()
            define_logging_options(opt)
            self.define(opt)
            opt.log_rotate_when = log.get('when', 'midnight')
            opt.log_to_stderr = log.get('log_to_stderr', False)
            opt.logging = log.get('level', 'INFO')
            opt.log_file_prefix = os.path.join(logdir, log['filename'])
            if log.get('backups'):
                opt.log_file_num_backups = log.get('backups')
            if opt.log_port_prefix:
                opt.log_file_prefix += ".%s" % options.port
            opt.log_rotate_interval = log.get('interval', 1)
            opt.log_rotate_mode = 'time'
            logger = logging.getLogger(log['name'])
            if not settings.DEBUG:
                logger.propagate = 0
            else:
                if not opt.log_to_stderr:
                    logger.propagate = 0
                else:
                    logger.propagate = 1
            enable_pretty_logging(options=opt, logger=logger)
            map(lambda h: h.setFormatter(LogFormatter(fmt=log.get("formatter", LogFormatter.DEFAULT_FORMAT),
                                                      color=settings.DEBUG)), logger.handlers)

    def define(self, options=options):
        """
        定义命令行参数,你可以自定义很多自己的命令行参数，或重写此方法覆盖默认参数
        :return:
        """
        try:
            # 增加timerotating日志配置
            options.define("log_rotate_when", type=str, default='midnight',
                           help=("specify the type of TimedRotatingFileHandler interval "
                                 "other options:('S', 'M', 'H', 'D', 'W0'-'W6')"))
            options.define("log_rotate_interval", type=int, default=1,
                           help="The interval value of timed rotating")

            options.define("log_rotate_mode", type=str, default='size',
                           help="The mode of rotating files(time or size)")
        except:
            pass
        options.define("port", default=8000, help="run server on it", type=int)
        options.define("settings", default='', help="setting module name", type=str)
        options.define("address", default='0.0.0.0', help='listen host,default:0.0.0.0', type=str)
        options.define("log_patch", default=True,
                       help='Use ProcessTimedRotatingFileHandler instead of the default TimedRotatingFileHandler.',
                       type=bool)

        options.define("log_port_prefix", default=None, help='add port to log file prefix.', type=bool)
        options.define("logging_dir", default='', help='custom log dir.')
        options.define("disable_log", default=True, help='disable tornado log function.')


def run(application=None, sockets=None, **kwargs):
    server = Server()
    server.load_all(application, sockets, **kwargs)
    server.start()
