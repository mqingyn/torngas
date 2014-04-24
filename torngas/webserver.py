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
from torngas.exception import ConfigError, TorngasError

reload(sys)
sys.setdefaultencoding('utf-8')
application_module = lazyimport('torngas.application')
settings_module = lazyimport('torngas.helpers.settings_helper')


class Server(object):
    settings = None
    urls = []
    application = None
    proj_path = None

    def init(self, project_path=None):
        self.load_define()
        tornado.options.parse_command_line()
        self.settings = settings_module.settings
        self.proj_path = project_path
        return self

    def load_define(self):
        define("port", default=8000, help="run server on it", type=int)
        define("setting", default='setting', help="""config used to set the configuration file type,\n
        settings_devel was default,you can set settings_functest or settings_production (it's your config file name)""",
               type=str)
        define("address", default='localhost', help='listen host,default:localhost', type=str)
        define("log_prefix", default='../log', help='log file dirname', type=str)
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
                raise TorngasError("urls not found.")

            self.application = application_module.Application(handlers=self.urls,
                                                              default_host='',
                                                              transforms=None, wsgi=False,
                                                              **self.settings.TORNADO_CONF)
        else:
            if isinstance(application, tornado.web.Application):
                self.application = application
            else:
                self.application = application(handlers=self.urls,
                                               default_host='',
                                               transforms=None, wsgi=False,
                                               **self.settings.TORNADO_CONF)

        self.application.project_path = self.proj_path \
            if self.proj_path.endswith('/') else self.proj_path + '/'

        tmpl = self.settings.TEMPLATE_CONFIG.template_engine
        self.application.tmpl = import_object(tmpl) if tmpl else None

        return self

    def load_urls(self, urls=None):
        if urls:
            self.urls = urls
            return self
        urls = []
        if self.settings.INSTALLED_APPS:
            for app_name in self.settings.INSTALLED_APPS:
                app_urls = import_object(app_name + '.urls.urls')

                for url in app_urls:
                    url.kwargs['subapp_name'] = app_name
                    url.name = '%s-%s' % (app_name, url.name,)
                urls.extend(app_urls)
        else:
            raise ConfigError('load urls error,INSTALLED_APPS not found!')
        self.urls = urls
        return self

    def load_logger_config(self):
        """
        重定义tornado自带的logger，可重写
        """

        config = self.settings.LOG_CONFIG
        from tornado.log import LogFormatter

        def enable_pretty_logging_path(options=None, logger=None):

            """Turns on formatted logging output as configured.

            This is called automaticaly by `tornado.options.parse_command_line`
            and `tornado.options.parse_config_file`.
            """

            if options is None:
                from tornado.options import options
            if options.logging == 'none':
                return
            if logger is None:
                logger = logging.getLogger()
            logger.setLevel(getattr(logging, options.logging.upper()))

            if options.log_file_prefix:
                channel = None
                rotating_handler = config['rotating_handler']
                if hasattr(logging.handlers, rotating_handler):

                    handler = getattr(logging.handlers, rotating_handler)
                    if rotating_handler == 'RotatingFileHandler':
                        channel = handler(
                            filename=options.log_file_prefix,
                            maxBytes=options.log_file_max_size,
                            backupCount=options.log_file_num_backups,
                            delay=config['delay'])

                    elif rotating_handler == 'TimedRotatingFileHandler':
                        channel = handler(
                            filename=options.log_file_prefix,
                            when=config['when'],
                            interval=config['interval'],
                            delay=config['delay'],
                            backupCount=options.log_file_num_backups)
                        channel.suffix = config['suffix']

                    if channel:
                        channel.setFormatter(LogFormatter(color=False))
                        logger.addHandler(channel)

            if (options.log_to_stderr or
                    (options.log_to_stderr is None and not logger.handlers)):
                # Set up color if we are in a tty and curses is installed
                channel = logging.StreamHandler()
                channel.setFormatter(LogFormatter())
                logger.addHandler(channel)

        options.logging = config["level"]
        options.log_to_stderr = config["log_to_stderr"]
        options.log_file_max_size = config["filesize"]
        options.log_file_num_backups = config["backup_num"]
        #tornado把默认的根logger加了handler
        #把根logger的handler去除，然后重新绑定在tornado的logger下
        logging.getLogger().handlers = []
        tornado_logpath = os.path.join(options.log_prefix,
                                       'tornado_access_log')

        if not os.path.exists(tornado_logpath):
            os.makedirs(tornado_logpath)

        file_name = "%s_access_log.%s.log" % ('tornado', str(options.port))
        options.log_file_prefix = os.path.join(tornado_logpath, file_name)
        enable_pretty_logging_path(options, logging.getLogger('tornado'))

        if hasattr(self.settings, 'LOG_RELATED_NAME'):

            for k, log in self.settings.LOG_RELATED_NAME.items():
                path = os.path.join(options.log_prefix, k)

                if not os.path.exists(path):
                    os.makedirs(path)

                options.log_file_prefix = os.path.join(path, "%s_log.%s.log" % (log, str(options.port)))
                enable_pretty_logging_path(options, logging.getLogger(log))
        return self

    def server_start(self, no_keep_alive=False, io_loop=None,
                     xheaders=False, ssl_options=None, protocol=None, sockets=None, **kwargs):
        if not sockets:
            try:
                addr = options.address
            except AttributeError:
                addr = '127.0.0.1'
            from tornado.netutil import bind_sockets

            if self.settings.IPV4_ONLY:
                import socket

                sockets = bind_sockets(options.port, addr, family=socket.AF_INET)
            else:
                sockets = bind_sockets(options.port, addr)

        http_server = tornado.httpserver.HTTPServer(self.application, no_keep_alive, io_loop,
                                                    xheaders, ssl_options, protocol, **kwargs)
        http_server.add_sockets(sockets)
        self.print_settings_info()

        tornado.ioloop.IOLoop.instance().start()

    def print_settings_info(self):

        if self.settings.TORNADO_CONF.debug:
            print 'tornado version: %s' % tornado.version
            print 'project path: %s' % self.proj_path
            print 'load middleware: %s' % list(self.settings.MIDDLEWARE_CLASSES).__str__()
            print 'debug open: %s' % self.settings.TORNADO_CONF.debug
            print 'locale support: %s' % self.settings.TRANSLATIONS
            print 'load apps:\n %s' % self.settings.INSTALLED_APPS.__str__()
            print 'IPV4_Only: %s' % self.settings.IPV4_ONLY
            print 'template engine: %s' % self.settings.TEMPLATE_CONFIG.template_engine
            print 'log file path: %s' % os.path.abspath(options.log_prefix)
            print 'server started. development server at http://%s:%s/' % ( options.address, options.port)

    def runserver(self, proj_path, application=None, urls=None):
        self.init(proj_path)
        self.load_urls(urls)
        self.load_application(application)
        self.load_logger_config()
        self.server_start()


