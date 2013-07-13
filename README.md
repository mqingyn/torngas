TornGas
=======

基于tornado的django like框架

增加了以下功能：
 * session支持：默认支持process cache，可使用memcache，redis，file等多种方式的session backend，依赖于cache模块
 * cache支持：基于django的cache模块，增加了redis缓存支持，缓存类型分为：file文件缓存，dummy缓存(nocache，仅实现接口，方便调试)，memcache,redis,本地缓存
 * 多线程异步handler：multithreading模块增加了对线程异步的支持
 * signals信号：来自django的signals模块
 * handler：内置webhandler和apihandler，webhandler对tornado的RequestHandler进行了扩展
 * mixin:增加了类似flask的FlashMixin，以及处理未捕获异常的错误页UncaughtExceptionMixin
 * torngas.utils:内置了来自web.py，django的部分实用utils
 * 中间件支持：默认自带一个session中间件，可自行编写和扩展中间件，只要继承实现middleware下的BaseMiddleware类即可
 * 配置文件：仿照django的配置文件方式，默认支持三份配置文件，devel，functest和production，根据config参数决定使用哪一个，方便线上线下的配置切换
 * 模板引擎：集成了jinja2和mako，可在配置文件中进行切换，根据喜好选择最合适的模板引擎

 torngas参考和借鉴了django,web.py,flask,mako,tinman,lepture,felinx等项目或作者的开源实现,在此十分感谢。


