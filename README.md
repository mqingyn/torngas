 #TornGas v0.2.5

基于tornado的django like框架

增加了以下功能：
 * session支持：默认支持process cache，可使用memcache，redis，file等多种方式的session backend，依赖于cache模块
 * cache支持：完全基于django的cache模块，增加了redis缓存支持，可参照django中关于cache部分的文档
 * 多线程异步handler：multithreading模块增加了对线程异步的支持，增加async_execute装饰器，可利用gen.Task提供基于线程池的异步操作(需安装futures库)
 * signals信号：来自django的signals模块
 * handler：内置webhandler和apihandler，webhandler对tornado的RequestHandler进行了扩展
 * mixin:提供了类似flask的FlashMixin，以及处理未捕获异常的错误页UncaughtExceptionMixin（tornado的404错误页我就不说了。。。）
 * utils:内置了部分实用函数
 * middleware：默认自带一个session中间件，可自行编写和扩展中间件，只要继承实现middleware下的BaseMiddleware类即可
 * templates：集成了对jinja2和mako的支持，可在配置文件中进行切换，根据喜好选择最合适的模板引擎
 * SQLAlchemy:对SQLAlchemy包装并集成了对SQLAlchemy的支持
 * basedb:源自web.py的db模块，感觉很好用（若使用basedb的连接池需安装DBUtils）
 * inject_factory：简单的对象绳命周期管理


目前框架还在持续迭代开发，还未形成一套比较好的文档，自愧不如。框架可能不够完善，欢迎拍砖，也算为开源
社区尽点微薄之力。


