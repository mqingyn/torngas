#!/usr/bin/env python
# -*- coding: utf-8 -*-
from torngas.helpers.route_helper import url, RouteLoader

route = RouteLoader(path='/')

urls = route.urlhelper('helloworld.views',
                       #也可以传递对象
                       url('Index', r'/', 'main_handler.Main')
)

if __name__ == '__main__':
    pass
