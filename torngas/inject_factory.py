#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
inject factory
eg:
factory.register('myObj',Object,POOLED)
obj=factory.resolve('myObj')
简单的依赖注入实现，业务类对象提供实例依赖控制和生存期管理
SINGLETON, TRANSIENT, POOLED, THREAD分别为注入对象的四种生命周期设置：
单例，临时，对象池，线程
通过factory的register方法注册对象类，使用factory.resolve方法获得该类实例。
单例方式在注册时即生成了类对象实例，在任何地方均得到同一个实例对象，不支持有参构造器的类
临时方式每次都会重新new()一个新对象
对象池模式，生成的对象会在对象池中保存，待下次使用。
线程模式，同一个线程下行为与对象池模式相同，不同线程会生成不同的对象实例
"""
import inspect
import hashlib
from torngas.utils import Null
from torngas.exception import ArgumentError
from torngas.utils.storage import ThreadedDict

_REGISTER_TABLE = {}
_FACTORY_CONTAINER = {}
_THREAD_CONTAINER = ThreadedDict()
SINGLETON, TRANSIENT, POOLED, THREAD = 0, 1, 2, 3

LIFECYCLE_TYPE = (SINGLETON, TRANSIENT, POOLED, THREAD)


class InjectFactory(object):
    def register(self, alias_name, module, lifecycle_type=POOLED):

        assert inspect.isclass(module), 'register must be a class object'
        if alias_name not in _REGISTER_TABLE:
            if lifecycle_type not in LIFECYCLE_TYPE:
                raise ArgumentError("lifecycle_type error.")
            _REGISTER_TABLE[alias_name] = (module,
                                           lifecycle_type )
            if lifecycle_type == SINGLETON:
                resolve_name = hashlib.md5(alias_name).hexdigest()
                _FACTORY_CONTAINER[resolve_name] = module()
        else:
            raise ArgumentError("alias_name '%s' already exists!" % alias_name)

    def resolve(self, alias_name, *args, **kwargs):

        if alias_name in _REGISTER_TABLE:
            service, lifecycle = _REGISTER_TABLE[alias_name]
        else:
            return Null()
        if lifecycle == TRANSIENT:
            return service(*args, **kwargs)
        if lifecycle == SINGLETON:
            resolve_name = hashlib.md5(alias_name).hexdigest()
            return _FACTORY_CONTAINER[resolve_name]
        else:
            resolve_name = hashlib.md5('_'.join([alias_name, repr(args), repr(kwargs)])).hexdigest()

        if lifecycle == THREAD:
            if resolve_name not in _THREAD_CONTAINER:
                _THREAD_CONTAINER[resolve_name] = service(*args, **kwargs)
            return _THREAD_CONTAINER[resolve_name]

        if lifecycle == POOLED:
            if resolve_name not in _FACTORY_CONTAINER:
                _FACTORY_CONTAINER[resolve_name] = service(*args, **kwargs)
            return _FACTORY_CONTAINER[resolve_name]


    def R(self, alias_name, *args, **kwargs):
        return self.resolve(alias_name, *args, **kwargs)


factory = InjectFactory()
if __name__ == '__main__':
    pass
