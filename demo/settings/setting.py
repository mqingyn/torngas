#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
# ###########
# 中间件  #
# ###########
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
MIDDLEWARE_CLASSES = (
    'torngas.middleware.accesslog.AccessLogMiddleware',
    'torngas.middleware.session.SessionMiddleware',
    'torngas.middleware.signal.SignalMiddleware',
    'torngas.httpmodule.httpmodule.HttpModuleMiddleware',
)
INSTALLED_APPS = (
    'helloworld',
)
# 全局modules配置
COMMON_MODULES = (
    # 'module限定名',
)
# 路由modules，针对某个路由或某些路由起作用
ROUTE_MODULES = {
    # '路由名称':['module限定名','!被排除的全局module限定名'],
}
# ##########
# 缓存配置 #
# ##########
CACHES = {
    'default': {
        'BACKEND': 'torngas.cache.backends.localcache.LocMemCache',
        'LOCATION': 'process_cache',
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCY': 3
        }
    },
    'default_memcache': {
        'BACKEND': 'torngas.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211'
        ],
        'TIMEOUT': 300
    },
    'dummy': {
        'BACKEND': 'torngas.cache.backends.dummy.DummyCache'
    },
    'filebased': {
        'BACKEND': 'torngas.cache.backends.filebased.FileBasedCache',
        'LOCATION': '.'
    },
    'default_redis': {
        'BACKEND': 'torngas.cache.backends.rediscache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
        'TIMEOUT': 3,
        'OPTIONS': {
            'DB': 0,
            # 'PASSWORD': 'yourredispwd',
            'PARSER_CLASS': 'redis.connection.DefaultParser'
        },
        'KEY_PREFIX': '',
        'VERSION': 1
    },

}


# ################
# 本地化翻译文件地址#
# ################

TRANSLATIONS = False  # 是否开启国际化
TRANSLATIONS_CONF = {
    'translations_dir': os.path.join(PROJECT_PATH, 'translations'),
    'locale_default': 'zh_CN',
    'use_accept_language': True
}

# tornado全局配置
TORNADO_CONF = {
    "static_path": "static",
    "xsrf_cookies": True,
    "debug": True,
    "xheaders": True,
    "login_url": '/login',
    "cookie_secret": "bXZ/gDAbQA+zaTxdqJwxKa8OZTbuZE/ok3doaow9N4Q=",
    "template_path": os.path.join(PROJECT_PATH, 'templates'),
    # 安全起见，可以定期生成新的cookie 秘钥，生成方法：
    # base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
}

# 白名单未开启，如需使用，请用元祖列出白名单ip
WHITELIST = False
# ######
# WHITELIST = (
# '127.0.0.1',
# '127.0.0.2',
# )

#tornado日志功能配置
LOGGER_CONFIG = {
    "tcp_logging_port": 9020,
    "tcp_logging_host": 'localhost',
    "root_logger_name": 'tornado',
    "level": 'DEBUG'
}
#####默认日志logger模块
#access log 访问日志统计
ACCESS_LOGGING_OPEN = True
ACCESS_LOGGING_NAME = 'tornado.torngas_accesslog'
ACCESS_LOGGING_FILE = os.path.join(PROJECT_PATH, "logs/torngas_access_log.log")
ACCESS_LOGGING_ROLLOVER_WHEN = "midnight"

#general log 错误，警告，和异常输出，**不要关闭这个log
GENERAL_LOGGING_OPEN = False
GENERAL_LOGGING_NAME = "tornado.torngas_generallog"
GENERAL_LOGGING_FILE = os.path.join(PROJECT_PATH, "logs/torngas_trace_log.log")
GENERAL_LOGGING_ROLLOVER_WHEN = "midnight"

#info log ，info和debug类型日志输出
INFO_LOGGING_OPEN = False
INFO_LOGGING_NAME = "tornado.torngas_infolog"
INFO_LOGGING_FILE = os.path.join(PROJECT_PATH, "logs/torngas_info_log.log")
INFO_LOGGING_ROLLOVER_WHEN = "midnight"
# 自定义类型logger,可配置多个
CUSTOM_LOGGING_CONFIG = {
    "CUSTOM_LOG": {
        "NAME": "tornado.torngas_customlog",  #必要
        "FILE": os.path.join(PROJECT_PATH, "logs/torngas_custom_log.log"),  #必要
        "ROLLOVER_WHEN": "midnight",
        "OPEN": False,  #必要
        "LOGGER": "mylogger.logger.customlog"  #必要
    }
}


########
IPV4_ONLY = True


#开启session支持
SESSION = {
    'session_cache_alias': 'default',  # 'session_loccache',对应cache配置
    'session_name': '__TORNADOSSID',
    'cookie_domain': '',
    'cookie_path': '/',
    'expires': 0,  # 24 * 60 * 60, # 24 hours in seconds,0代表浏览器会话过期
    'ignore_change_ip': False,
    'httponly': True,
    'secure': False,
    'secret_key': 'fLjUfxqXtfNoIldA0A0J',
    'session_version': 'EtdHjDO1'
}

# 用编译的正则表达式来限定user-agent，来自django，可参考django的处理方式
# example:
# import re
# DISALLOWED_USER_AGENTS = (
#     re.compile(r'^NaverBot.*'),
#     re.compile(r'^EmailSiphon.*'),
#     re.compile(r'^SiteSucker.*'),
#     re.compile(r'^sohu-search')
# )
DISALLOWED_USER_AGENTS = ()
#为所有的url移除尾部'/'
#依赖common_middleware
REMOVE_SLASH_ALL = False

# 是否开启对包含非法字符的请求做403处理
# 若启用请先引入torngas.middleware.common.CommonMiddleware
ILLEGAL_CHARACTER_FORBIDDEN = False
# 当启用非法请求处理时，请填写非法字符列表#
ILLEGAL_CHARACTER = ()


#配置模版引擎
#引入相应的TemplateLoader即可
#若使用自带的请给予None
#支持mako和jinja2
#mako设置为torngas.template.mako_loader.MakoTemplateLoader
#jinj2设置为torngas.template.jinja2_loader.Jinja2TemplateLoader
#初始化参数请参照jinja的Environment或mako的TemplateLookup,不再详细给出
TEMPLATE_CONFIG = {
    'template_engine': None,
    #模版路径由torngas.handler中commonhandler重写，无需指定，模版将存在于每个应用的根目录下
    'filesystem_checks': True,  #通用选项
    'cache_directory': '../_tmpl_cache',  #模版编译文件目录,通用选项
    'collection_size': 50,  #暂存入内存的模版项，可以提高性能，mako选项,详情见mako文档
    'cache_size': 0,  #类似于mako的collection_size，设定为-1为不清理缓存，0则每次都会重编译模板
    'format_exceptions': False,  #格式化异常输出，mako专用
    'autoescape': False  #默认转义设定，jinja2专用

}


# 数据库连接字符串，
# 元祖，每组为n个数据库连接，有且只有一个master，可配与不配slave
DATABASE_CONNECTION = {
    'default': {
        'kwargs': {'pool_recycle': 3600},
        'connections': [{
                            'ROLE': 'master',
                            'DRIVER': 'mysql+mysqldb',
                            'UID': 'root',
                            'PASSWD': '',
                            'HOST': '',
                            'PORT': 3306,
                            'DATABASE': '',
                            'QUERY': {"charset": "utf8"}

                        },
                        {
                            'ROLE': 'slave',
                            'DRIVER': 'mysql+mysqldb',
                            'UID': 'root',
                            'PASSWD': '',
                            'HOST': '',
                            'PORT': 3306,
                            'DATABASE': '',
                            'QUERY': {"charset": "utf8"}

                        }]
    }
}

# sqlalchemy配置，列出部分，可自行根据sqlalchemy文档增加配置项
# 该配置项对所有连接全局共享
SQLALCHEMY_CONFIGURATION = {
    'echo': True,
    'max_overflow': 10,
    'echo_pool': True,
    'pool_timeout': 10
}