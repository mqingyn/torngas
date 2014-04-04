#!/usr/bin/env python
# -*- coding: utf-8 -*-
from torngas.helpers.route_helper import url, RouteLoader

route = RouteLoader(path='/')

urls = route.urlhelper('helloworld.views',
    url('Index', r'/', 'main_handler.Main') #也可以传递对象
)

if __name__ == '__main__':
    pass
