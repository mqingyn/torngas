#-*-coding=utf-8-*-
import os
############
#   中间件  #
############
MIDDLEWARE_CLASSES = (
    'torngas.middleware.SessionMiddleware',
)

############
# 加载的应用 #
############
INSTALLED_APPS = (
    'Main',

)


############
#应用的html模板路径
###########
APPS_TEMPLATES_DIR = {
    'Main': 'Main/templates'

}

###########
# 缓存配置 #
###########
CACHES = {
    'default': {
        'BACKEND': 'torngas.cache.backends.localcache.LocMemCache',
        'LOCATION': 'process_cache',
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCY': 3
        }
    },
    'session_loccache': {
        'BACKEND': 'torngas.cache.backends.localcache.LocMemCache',
        'LOCATION': 'process_session',
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCY': 3
        }

    },
    'memcache': {
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
    'redis_cache': {
        'BACKEND': 'torngas.cache.backends.rediscache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
        'TIMEOUT': 3,
        'OPTIONS': {
            'DB': 0,
            # 'PASSWORD': 'yadayada',
            'PARSER_CLASS': 'redis.connection.DefaultParser'
        },
        'KEY_PREFIX': '',
        'VERSION': 1
    },

}


#################
#本地化翻译文件地址#
#################

TRANSLATIONS = False #是否开启国际化
TRANSLATIONS_CONF = {
    'translations_dir': os.path.join(os.path.dirname(__file__), 'translations'),
    'locale_default': 'zh_CN',
    'use_accept_language': True
}

#tornado全局配置
TORNADO_CONF = {
    "static_path": "/var/www/static",
    "xsrf_cookies": True,
    "debug": True,
    "xheaders": True,
    "login_url": '/login',
    "cookie_secret": "bXZ/gDAbQA+zaTxdqJwxKa8OZTbuZE/ok3doaow9N4Q="
    #安全起见，可以定期生成新的cookie 秘钥，生成方法：
    #base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
}

#白名单未开启，如需使用，请用元祖列出白名单ip
WHITELIST = False
#######
# WHITELIST = (
#     '127.0.0.1',
# '127.0.0.2',
# )

#tornado日志功能配置
LOG_CONFIG = {
    'path': '../log', #日志记录路径
    'level': 'info', #日志级别
    'filesize': 1000 * 1000 * 1000, #日志文件大小限制
    'backup_num': 5, #最多保留文件数
    'log_to_stderr': True
}

IPV4_ONLY = True

#开启session支持
SESSION = {
    'session_cache_alias': 'session_loccache', # 'session_loccache',对应cache配置
    'session_name': '__TORNADOID',
    'cookie_domain': '',
    'cookie_path': '/',
    'expires': 0, # 24 * 60 * 60, # 24 hours in seconds,0代表浏览器会话过期
    'ignore_change_ip': False,
    'httponly': True,
    'secure': False,
    'secret_key': 'fLjUfxqXtfNoIldA0A0J',
    'session_version': 'v1'
}

#配置模版引擎
#引入相应的TemplateLoader即可
#若使用自带的请给予None
#支持mako和jinja2
#mako设置为torngas.template.mako_loader.MakoTemplateLoader
TEMPLATE_ENGINE = 'torngas.template.jinja2_loader.Jinja2TemplateLoader'

TEMPLATE_CONFIG = {
    ########### mako 配置项 使用mako时生效###########
    #模版路径由torngas.handler中commonhandler重写，无需指定，模版将存在于每个应用的根目录下
    'filesystem_checks': False, #通用选项
    'cache_directory': '/tmp/_tmpl_cache', #模版编译文件目录,通用选项
    'collection_size': 50, #暂存入内存的模版项，可以提高性能，mako选项,详情见mako文档
    'cache_size': 0, #类似于mako的collection_size，设定为-1为不清理缓存，0则每次都会重编译模板
    'format_exceptions': True, #格式化异常输出，mako专用
    'autoescape': False #默认转义设定，jinja2专用
    ###########      end        ##################
}


# 数据库连接字符串，
# 元祖，每组为n个数据库连接，有且只有一个master，可配与不配slave
DATABASE_CONNECTION = {

    'aquis': {
        'kwargs': {'pool_recycle': 3600},
        'connections': [{
                            'ROLE': 'master',
                            'DRIVER': 'mysql+mysqldb',
                            'UID': 'root',
                            'PASSWD': 'root',
                            'HOST': '127.0.0.1',
                            'PORT': 3306,
                            'DATABASE': 'your database',
                            'QUERY': {"charset": "utf8"}

                        },
                        {
                            'ROLE': 'slave',
                            'DRIVER': 'mysql+mysqldb',
                            'UID': 'root',
                            'PASSWD': 'root',
                            'HOST': '127.0.0.1',
                            'PORT': 3306,
                            'DATABASE': 'your database',
                            'QUERY': {"charset": "utf8"}

                        }]
    }
}





# sqlalchemy配置，列出部分，可自行根据文档增加配置项
# 该配置项对所有连接全局共享
SQLALCHEMY_CONFIGURATION = {
    'echo': True,
    'max_overflow': 10,
    'echo_pool': True,
    'pool_timeout': 1
}