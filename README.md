#Torngas Web Framework
A simple app web framework based on tornado.

[![Build Status](https://travis-ci.org/mqingyn/torngas.svg?branch=master)](https://travis-ci.org/mqingyn/torngas)

###version:1.8.0

Torngas 是基于[Tornado](https://github.com/tornadoweb/tornado)的web mvc框架。Torngas 大量参考和借鉴了Django的设计模式，形成一套基于tornado的Django like应用层开发框架。tornado 建议使用4.0以上版本,注意：torngas不支持基于WSGI的应用。



##**框架依赖**

* future
* tornado>=3.2

##**安装**

 * **pip**:  `pip install torngas`

##**快速入门**

* 导引：

	* [目录结构](#user-content-目录结构示例)
 	* [settings 配置](#user-content-settings配置)
 	* [webserver](#user-content-webserver)
 	* [app](#user-content-app)
 	* [urls](#user-content-urls)
 	* [log](#user-content-log)
 	* [模板引擎](#user-content-模板引擎)
 	* [handler](#user-content-handler)
 	* [中间件](#user-content-中间件)
 	* [HTTP处理器](#user-content-http处理器)
 	* [缓存](#user-content-缓存)
 	* [db&orm](#user-content-dborm)
 	* [线程池异步](#user-content-异步线程池)
 	* [session](#user-content-session)
 	* [signal](#user-content-signal)
 	
<br>

* ####目录结构示例：

        |- app
            +- myapp1
            |   |- urls.py
            |   |- handlers
            |       |- hello_china.py
            |       |- hello_usa.py
            |       |- ...
            |          
            +- myapp2
            |   |- ...
            |
            +- logs
            |
            +- middlewares
            |   |- ...
            |
            +- settings
            |   |- settings.py
            |   |- settings_online.py
            |
            +- httpmodules
            |   |- ...
            |
            +- templates
            |   |- ...
            |
            +- statics
            |   |- ...
            +- runserver.py
                

  * helloworld :
	
		你可以参考demo目录下的 `helloworld` 项目示例，并运行：
		
			python demo/runserver.py --address=0.0.0.0 --port=8000 --settings=settings.setting

		启动服务后，在浏览器中查看 `127.0.0.1:8000` ,你应该可以看到一个欢迎页面！


* ####settings配置：
	
	在项目runserver.py中，你可以指定使用的预设值的默认配置文件，如配置文件在应用根目录app.settings下的setting.py：

		os.environ.setdefault('TORNGAS_APP_SETTINGS', 'settings.setting')

	在程序启动时，首先会检查 `--settings=` 是否给定如`--settings=settings.setting`，框架将自动加载应用目录下settings模块中的setting.py配置文件，如果未规定，则使用以上预设值默认配置。在项目中使用配置：

		from torngas import settiings
		
		project_path = settings.PROJECT_PATH

	*version 1.6.7 add* :
	
	`DEBUG`: 控制应用是否处于debug状态，等同于 tornado的debug参数。  
	`XHEADERS`： 控制是否开启httpserver的 xheaders。你不用再额外传递一个xheader参数。

* ####webserver:
	
	最简单的server启动方式：
		
		from torngas.webserver import run
    	run()

	这将启动一个默认的tornado进程，如果想控制更多细节，你可以：
		
		from torngas.webserver import Server
		from tornado.options import define
		define("your_arg", default='default', help='your command args', type=str)
		
		serv = Server()
		serv.parse_command() #你必须调用parse_command()来处理tornado options,否则无法加载配置
		serv.load_urls()
    	serv.load_application(application=None) # 或根据你的需求自定义Application
    	serv.server_start(sockets=None, **kwargs)

	很多情况下，我们希望对Application对象进行个性化的处理，通常，我们习惯于实现一个Application子类：

	*version 1.6.7 add*:

		from torngas.application import Application
	
		class MyApp(Application):
			"""your custom code"""

		Server().load_application(MyApp)
		...

	`load_application` 接收一个 `torngas.applicatoin.Application` 类实例或其子类

	>如果要使用torngas的全部功能，你的自定义 `application` 不能直接继承于 `tornado.web.Application` 。


		

	>Server对象的 `server_start`，`load_all` 以及 `torngas.run` 支持自定义的 `httpserver` 参数
	>        
	>        Server().server_start(no_keep_alive=True,backlog=512)

	*version 1.6.7 add* :

	`server.load_all` ：如果你希望控制一些细节，但是又希望更简单的启动服务 , `load_all()` 会是更好的选择。 

		serv = Server()
		serv.load_all(application=MyApp,no_keep_alive=True,backlog=512)
		serv.start()
	
	>与 `server_start` 不同的是，load_all，以及 `torngas.run` 会帮你自动 `parse_command`,处理tornado.options ,所以不需要手动调用它。其他方式你需要手动调用 `parse_command` 。


	`parse_command`: Server对象的 `parse_command` 方法的作用等同于 tornado 中的 `parse_command_line` 同时为你初始化 log日志配置,你必须放在 `define` 语句之后调用，否则定义的参数将不起作用。
		
	>你可能注意到 `start` 方法，这个方法类似于ioloop.start ,同时在debug模式下打印一些基础启动信息。 `server_start` 还会帮你处理httpserver的加载。所以，当你使用server_start时，不需要在调用 `start`方法或 `ioloop.start()`。

	>当你使用 `load_all` 来载入 `application` 和  `httpserver` 时，使用 `start` 是更好的选择 。
		
* ####app:
	
	如顶述目录结构，您可以在应用根目录下创建多个app模块，假如你建立了应用myapp1，应用目录中**必须**包含 `urls.py`。
	同时，要加载你的应用，你需要在配置文件中 `INSTALLED_APPS` 元组中增加你的app配置，如你的应用根目录app下存在myapp1，myapp2，则需：

		INSTALLED_APPS = (
			'myapp1',
			'myapp2',				
		)

	系统启动后，将自动加载myapp1,myapp2中的urls.py下的路由配置。

* ####urls:

	每一个app都必须包含一个urls.py的路由表文件。你可以像这样配置路由：

		from torngas import Url, route

		u = Url('myapp1.handlers',abc='abc')
		urls = route(
		    u(name='Index', pattern=r'/?', handler='main_handler.Main'),
			u(name='Login', pattern=r'/login/?', handler='main_handler.Login'),
			u(name='User', pattern=r'/user/?', handler='main_handler.User'),
		)

	Url()接受参数 `prefix` 模块前缀，上述例子中最终的加载handler模块为： `myapp1.handlers.main_handler.Main`.
	Url()还可以接受若干全局预加载参数。其作用等同于tornado 路由的kwargs参数，此参数将会被解析到每个handler的\_url_kwargs变量中,如上述abc='abc'。
		
	main_handler.Main:

		from torngas.handler import WebHandler
		class Main(WebHandler):
			def get(self):
				self.finish(self._url_kwargs['abc']) # print abc


	每一个url还可以接受一个kwargs参数，这个参数仅对当前路由有效，其作用等同于上述的_url_kwargs，同样会被解析到\_url_kwargs字典中。如果遇到同名参数，路由的kwargs会覆盖Url()中定义的同名参数，但仅影响当前路由。

		u(name='User', pattern=r'/user/?', handler='main_handler.User'，kwargs={'abc':'other'}),

	你也可以直接import对应的handler:
		
		from myapp1.handlers.main_handler import Main
		u = Url()
		urls = route(
		    u(name='Index', pattern=r'/?', handler=Main),
		)

	*路由分组*：
		当你有许多路由时，为了便于管理，你可以将路由分散到多个文件中：
		
		url_photo.py:

		url=Url('myapp1.handlers')
        URLS = route(
            url(r'photo/upload/?','photo.UploadHandler'),
            ...
        )

		url_blog.py:

        url=Url('myapp1.handlers')
        URLS = route(
            url(r'blog/list/\d*/?','blog.ListHandler'),
            ...,
            
        )
		urls.py:

		from torngas import route
		from myapp1.url_blog import URLS as blog_urls

		url = Url('myapp1.handlers')
	    URLS = route(
			include('/','myapp1.url_photo.URLS'),
			include('/',blog_urls),
			url(r'/user/me/?','user.MeHandler'),
		)
	
* ####log：
    ###### version add:1.8.0  
	torngas支持使用原生tornado日志模块，或torngas基于logging扩展日志，torngas默认启用扩展日志代替tornado默认的log，除非`--disable_log＝False` ,则启用tornado.log模块 。

		from torngas.logger import syslogger
		
		syslogger.error("this is a error.")

	日志配置中的默认日志HANDLER默认为 `torngas.logger.ProcessLogTimedFileHandler` ,此handler支持在多进程状态下安全的写入日志文件，如需日志文件名按照端口号区分，通过设置 `--log_port_prefix＝true` , `--logging_dir` 如果设定， 配置文件中的 `LOGGING_DIR` 将被忽略。 
	
	你可以自定义你的日志配置，或新增日志，你只需要在LOGGING配置中加入类似段落：

		        {
        'name': 'tornado',
        'level': 'INFO',
        'log_to_stderr': False,
        'when': 'midnight',
        'interval': 1,
        'filename': 'tornado.log'
        },
	
	> 注：请保留默认的几个日志配置。

	

* ####模板引擎：

	在配置文件 `TEMPLATE_CONFIG` 中配置模板。 其中，`template_engine` 决定使用什么模板加载器(Loader) ,默认为 None，使用自带的模板引擎。 可选择使用 mako 或 jinja2 ，*需要安装依赖库 mako或jinja2* 。

		TEMPLATE_CONFIG = {
		    'template_engine': 'torngas.template.mako_loader.MakoTemplateLoader' #使用mako模板
		    'filesystem_checks': True,  # 通用选项
		    'cache_directory': '../_tmpl_cache',  #通用选项，模版编译临时文件目录
		    'collection_size': 50,  #mako选项,暂存入内存的模版项，可以提高性能，详情见mako文档
		    'cache_size': 0,  #jinja选项，类似于mako的collection_size，设定为-1为不清理缓存，0则每次都会重编译模板
		    'format_exceptions': False,  #mako选项，格式化异常输出
		    'autoescape': False  #jinja2选项，默认转义设定
			# 支持mako或jinja其他配置参数，详见相关文档。
		
		}

* ####handler：
	
	如果需要使用torngas提供的功能，业务handler需要继承自 `torngas.handler.WebHandler`或 `torngas.handler.ApiHandler` .
	
	WebHandler提供了兼容mako,jinja2模板引擎加载,中间件hook的功能。并额外提供两个方法 `on_prepare` 和 `complete_finish` ,
	这两个方法分别在 `prepare` 和 `on_finish` 方法执行结束后调用。
	
	同时，torngas提供了一个 `FlashMessageMixIn` ，可以配合handler实现消息闪现的功能,其作用类似flask中的flash。你的handler需要继承 `FlashMessageMixIn` ：
	
		class MyHandler(FlashMessageMixIn,WebHandler):
			
			def get(self):
				self.flash("Welcome back, %s" % username, 'success')
	
		base.html
		------------

		{% set messages = handler.get_flashed_messages() %}
		{% if messages %}
		<div id="flashed">
			{% for category, msg in messages %}
			<span class="flash-{{ category }}">{{ msg }}</span>
			{% end %}
		</div>
		{% end %}
	

* ####中间件：

	torngas实现了简单的中间件功能，其行为和功能类似于 Django 的中间件。在这里引用一张Django中间件的流程图：

	![Django中间件流程](https://docs.djangoproject.com/en/1.5/_images/middleware.png)




	我们可以参考这张图来理解torngas的中间件设计。torngas中间件遵循了类似于Django中间件的设计，但因为框架本身的差异性，torngas中间件
	采用对RequestHandler执行流程中插入hook的方式，中间件默认没有返回值，你可以在需要的请求阶段对请求对象(request或handler)进行处理。
	
	>*注：要使用中间件功能，你的handler必须继承自 `torngas.handler.WebHandler` 或 `torngas.handler.ApiHandler`


	自定义中间件：

		class MyMiddleware(object):
		    def process_init(self, application):
		        """
		        :param application: 应用程序对象，此方法在tornado启动时执行一次
		        """
		    def process_call(self, request, clear):
		        """
		        在请求request对象创建时，参数为请求对象，此时还未匹配路由handler
		        :param request: 请求对象
		        """
		    def process_request(self, handler, clear):
		        """
		        匹配路由后，执行处理handler时调用
		        :param handler: handler对象
		        支持异步
		        """
		    def process_render(self, handler, clear, template_name, **kwargs):
		        """
		        此方法在调用render/render_string时发生
		        :param handler: handler对象
		        :param template_name: 模板名称
		        :param kwargs: 模板参数
		        """
		    def process_response(self, handler, clear, chunk):
		        """
		        请求结束后响应时调用，此方法在render之后，finish之前执行，可以对chunk做最后的封装和处理
		        :param handler: handler对象
		        :param chunk : 响应内容，chunk为携带响内容的list，你不可以直接对chunk赋值，
					可以通过chunk[index]来改写响应内容，或再次执行handler.write()
		        """
		    def process_endcall(self, handler, clear):
		        """
		        请求结束后调用，此时已完成响应并呈现用户，一般用来处理收尾操作，清理缓存对象，断开连接等
		        :param handler: handler对象
		        """
	
			def process_exception(self,handler, clear, typ, value, tb):
		        """
		        请求过程引发异常时调用，你可以通过这个方法捕获在请求过程中的未捕获异常
				如果没有中间件实现此方法，则调用tornado RequestHandler.log_exception方法。
		        :param handler: handler对象
				:param typ: 等同RequestHandler.log_exception的参数，异常类型值和异常堆栈信息
				:param value:异常值信息
				:param tb:异常堆栈
		        """
	编写中间件需实现其中任何一个方法即可，中间件的执行流程中在请求阶段，`call` , `request` 按照中间件的声明**顺序执行**，
    在响应过程中，`exception`，`response` ，`endcall` 和 `render` 则是按声明顺序**倒序执行**） , 在tornado 4.0 中，`process_request`
    支持异步调用。

    在中间件中返回任意真值，如 return 1，则停止当前请求的其余中间件相同方法的执行，进入下一个中间件流程。特别是当finish请求后，需return 1，例如：

		def process_request(self, handler, clear):
			if not handler.user:
				handler.finish('auth failure.')
				return 1 
	
	调用finish后必须返回真值，`return 1`，这样会跳过剩余中间件的`process_request`方法，直接进入`finish`阶段 ，否则将继续执行 其余中间件`process_request`方法，以及`get/post`方法。

    clear: 如果希望当前请求剩余的所有中间件流程完全终止，则在方法头部调用此方法，以清空中间件的执行队列
            与return 1不同，clear() 会导致其余的中间件全部方法在该请求中**失效**，而return 1只会导致所有中间件的当前流程方法失效。

	默认提供的中间件：
		
	* `torngas.middleware.accesslog.AccessLogMiddleware` :定制处理日志打印
	* `torngas.middleware.dbalchemy.DBAlchemyMiddleware`：使用SqlAlchemy需要引入该中间件
	* `torngas.middleware.session.SessionMiddleware`：提供session功能
	* `torngas.middleware.session.SignalMiddleware`：事件信号通知中间件，对django的signal封装

	中间件配置：
		`MIDDLEWARE_CLASSES` :实现中间件需要在配置文件中加入。其顺序决定中间件请求处理的顺序。
	例如：


		MIDDLEWARE_CLASSES = (
			# access_log中间件放在最上面，因为在响应阶段，最上边的中间件处理方法process_endcall会在最后执行。
		    'torngas.middleware.accesslog.AccessLogMiddleware',
		    'torngas.middleware.session.SessionMiddleware',
		    'torngas.httpmodule.httpmodule.HttpModuleMiddleware',
		)
	


* ####HTTP处理器：

	中间件提供了对请求处理流程的干预能力，使得我们可以控制请求过程中的各个方面。但是我们无法从容的对特定请求的特定过程进行干预。HTTP处理器提供了路由级别的请求处理能力。HTTP处理器分为两种： `全局处理器` 和 `路由处理器` 。
	
	你需要在中间件中加入 `torngas.httpmodule.httpmodule.HttpModuleMiddleware` 启用路由处理功能。

	自定义HTTP处理器模块需要继承自 `torngas.httpmodule.BaseHttpModule` ,并实现 `begin_request`， `begin_render` , `begin_response` , `complete_response` 中任意一个方法即可，方法行为和功能类似中间件，同样，
	`begin_request` 方法在tornado4.0以上版本支持异步调用。

	HTTP处理器配置：


	* 全局处理器：通用路由处理器会处理所有请求的对应过程。行为等同于中间件，但是不同的是，在响应阶段，处理方法不同于中间件是倒序执行，而是**顺序执行**，同时需要注意的是，全局处理器总是优先于路由处理器之前执行。


			COMMON_MODULES = ( 
				'httpmodule.auth.AuthModule',
				'httpmodule.ipauth.ipblack',
			)
	
	* 路由处理器：根据配置在具体的路由请求中使用，格式为 `'正则path或路由name':['module1','!module2',]`。

			
			ROUTE_MODULES = {
			     '^/user/.*$':['httpmodule.loginmodule','!httpmodule.ipauth.ipblack',],
			     'Index': ['!httpmodule.auth.AuthModule',]
			}

		路由处理器为一个字典，字典的键为需要匹配的路由的名称(定义urls时指定)，或路由path的正则表达式，如上例。
		值为处理该路由请求的模块。
		在请求过程中，满足匹配条件的路由处理器将被在指定过程触发，根据模块实现的方法来进行相应的处理。 如果在配置模块的前面添加了 `!` 符号，将反选在`COMMON_MODULES`中同名的模块，那么在请求过程中，全局处理器将不再匹配的路由中执行。
		
		* 当你需要对某个路由禁用全部的 `COMMON_MODULES` 模块处理器时，你不需要写很多！，你只需要配置一条 `!all` 即可：
			
				ROUTE_MODULES = {
				     '^/user/.*$':['httpmodule.loginmodule','!all',],
				}
			`!all` 将会禁用 `COMMON_MODULES` 定义的全部处理器。由于 `COMMON_MODULES` 总是优先于路由处理器顺序执行，通过`!all`可以让你在 `ROUTE_MODULES` 中个性化你的路由处理器执行顺序，而其他的路由处理器配置不受影响。

			>注： 在路由处理器配置中添加 `!` 符号的处理器，必须存在于 `COMMON_MODULES` 中，否则将引起异常。

		如上实例中，请求名为Index 的路由将不执行 `COMMON_MODULES` 中配置的 `httpmodule.auth.AuthModule` 模块，请求满足 `^/user/.*$` 正则的路由不执行 `httpmodule.ipauth.ipblack` 模块。


* ####缓存：

	torngas支持使用memcache，redis，file，localcache作为缓存。缓存模块主要抽取自django.cache，相关配置可参考 Django文档，redis是新增支持。

	* redis缓存模块配置，例如：
	
		    'rediscache': {
		        'BACKEND': 'torngas.cache.backends.rediscache.RedisCache',
		        'LOCATION': '127.0.0.1:6379',
		        'OPTIONS': {
		            'DB': 0,
		            'PARSER_CLASS': 'redis.connection.DefaultParser',
		            'POOL_KWARGS': {
		                'socket_timeout': 2,
		                'socket_connect_timeout': 2
		            },
		            'PING_INTERVAL': 120  # 定时ping redis连接池，防止被服务端断开连接（s秒）
		        }
		    },	

		redis配置中，BACKEND	支持两种： 
				
		`torngas.cache.backends.rediscache.RedisCache` 和   `torngas.cache.backends.rediscache.RedisClient`。

		`RedisClient`提供一个原生的client属性，提供基础的，原生的redis-py功能,而`RedisCache` 继承自 `RedisClient` 是提供高层缓存使用，其实现了和 `torngas.cache.backends.memcached.MemcachedCache`相同的接口，且行为和功能一致。如果你需要一些高级的redis方法，请使用RedisClient，如果仅仅需要基础的缓存功能，使用RedisCache即可。RedisCache同样提供client属性。

* ####DB&ORM：

	torngas提供了对SqlAlchemy ORM的支持，模块`torngas.db.dbalchemy`对sqlalchemy进行了基本的封装使其更加易用。同时，torngas提供了一个简单轻量级的db模块basedb，此模块来自与web.py框架的db模块，基本的使用方式可以参考[web.py cookbook](http://webpy.org/cookbook/index.zh-cn),下面主要介绍dbalchemy模块。

	数据库配置：

		DATABASE_CONNECTION = {
		    'default': {
		        'connections': [{
		                            'ROLE': 'master',#主库
		                            'DRIVER': 'mysql+mysqldb',
		                            'UID': 'root',
		                            'PASSWD': '',
		                            'HOST': '',
		                            'PORT': 3306,
		                            'DATABASE': '',
		                            'QUERY': {"charset": "utf8"}
		
		                        },
		                        {
		                            'ROLE': 'slave',#从库，可配置多个
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
	
	
		
	`PING_DB`：定时对数据库进行ping操作，保持连接池可用。默认：500s
	
	 sqlalchemy配置，列出部分，可自行参考sqlalchemy文档增加配置项，该配置项对所有连接全局共享。

		SQLALCHEMY_CONFIGURATION = {
		    'sqlalchemy.connect_args': {
					'connect_timeout': 3 
			 },
		    'sqlalchemy.echo': False, #开启打印sql日志
		    'sqlalchemy.max_overflow': 10,
		    'sqlalchemy.echo_pool': False,
		    'sqlalchemy.pool_timeout': 5,
		    'sqlalchemy.encoding': 'utf-8',
		    'sqlalchemy.pool_size': 100,
		    'sqlalchemy.pool_recycle': 3600,
		    'sqlalchemy.poolclass': 'QueuePool'  # 手动指定连接池类
		}

	使用方式：
		
		from torngas.db.dbalchemy import Model
		from sqlalchemy import *
		from sqlalchemy.dialects.mysql import INTEGER
		
		
		class BaseModel(Model):
		    __abstract__ = True
		    __connection_name__ = 'default' #对应配置中的default项
		
		    ID = Column('id', INTEGER(11, unsigned=True), primary_key=True, nullable=False)  # primary key


		class User(BaseModel):

		    __tablename__ = 'users'
		
		    name = Column(String(10), nullable=False)
		    password = Column(String(64), nullable=False)


	* 查询：如上，Model对象的`Q`属性提供一个默认简单的查询对象，你可以像这样 `User.Q.filter(User.name='jack').all()` 。
	也可以像这样：`User.session.query(User)` 使用session属性创建查询对象。
	
	>当存在主从数据库时，执行增删改操作需要指明使用主库的会话对象： `session = User.session.using_master()`

	* 分页：

			query = User.Q.all()  
	        pagelist_obj = query.paginate(page=1, per_page=10, default=None)  
			total = pagelist_obj.total  
			page = pagelist_obj.page  
			items = pagelist_obj.items

	>使用Sqlalchemy必须在配置中间件中加入：**torngas.middleware.dbalchemy.DBAlchemyMiddleware**
		

* ####异步线程池

	tornado本身是异步单线程单进程框架，这样当遇到使用mysql的慢查询时，就会阻塞进程。torngas提供一个简单的方式来用线程池包装同步方法。通过配置文件设定
	`THREADS_NUM` 数量来决定线程池的最大线程数，默认为cpu_count。

	>注：新版tornado中内置了 `concurrent.run_on_executor` 装饰器，可提供同样的功能,torngas提供  `torngas.decorators.async_execute` 来方便使用线程池来异步化你的同步方法。

			from torngas.decorators.async_execute import async_execute
			class Test(Base):
			    @coroutine
			    def get(self):
			        a=''
			        b=''
			        #支持使用gen的task模块来同步化异步调用
			        result = yield self.dosomething(a, b)
			        self.finish(result)
			
			    @async_execute
			    def dosomething(self,a,b):
			        # 这里可能耗时很久
			        # something...
			        result='return'
			        return result


* ####session：

	torngas提供一个简单的session功能，session可以使用torngas.cache下的缓存模块或实现了 `torngas.cache.backends.base.BaseCache` 的模块类作为session_store,比如你可以使用memcache、redis或LocalCache缓存来作为session的存储。
	
	首先，你需要增加中间件 `torngas.middleware.session.SessionMiddleware` 来开启对session的支持，在具体的路由handler中，可以通过handler.session获取session存储对象。
	
	session配置：

		SESSION = {
		    'session_cache_alias': 'default',  # 'session_loccache',对应cache配置名
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

	session使用：
		你可以像这样读写session：
		
			class LoginHandler(WebHandler):
				def get(self,uid):
					self.session['userid'] = uid
					self.set_expire(3600 * 24 * 30) #30天

			class AuthHandler(WebHandler):
				def get(self,uid):
					uid = self.session['userid']

			class LogoutHandler(WebHandler):
				def get(self,uid):
					del self.session['userid']

* ####signal:

	信号组件提供信号的注册与通知处理能力，我们可以在任何地方注册事件，也可以在你希望的任何时候触发事件。在信号触发时，将调用接收信号的callback，进行相关业务逻辑处理。
	
	torngas提供了几个与请求过程相关的信号，这几个信号通过信号中间件触发。他们分别是 `call_started` ,`handler_started` , `handler_response` , `call_finished` , `handler_render` ,触发事件分别对应中间件 `process_call` , `process_request` , `process_response` , `process_endcall` , `process_render` 几个过程 。

	使用：
		
		from torngas.signal import call_started,handler_render

		class MyService(object):

			# 通过装饰器来注册事件回调
		    @receiver(call_started)
		    def callback(**kwargs):
		        """do something..."""

		def callback(**kwargs):
    		print kwargs

		# 通过调用信号connect方法注册事件回调
		handler_render.connect(callback)

	事件回调函数接收一个 `**kwargs` 参数，在事件触发时，kwargs包含事件的 signal对象，事件源的class，事件参数等。

	自定义信号事件：

		from dispatch import Signal
			
		my_event = Signal(providing_args=["args1"])

		# 事件触发
		my_event.send(sender=somesender.__class__, args1=arg)


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/mqingyn/torngas/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

