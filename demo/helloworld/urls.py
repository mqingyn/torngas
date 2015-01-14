# !/usr/bin/env python
# -*- coding: utf-8 -*-
from torngas import Url, route

u = Url('helloworld.handlers',abc='abc')
urls = route(
    u(name='Index', pattern=r'/', handler='main_handler.Main')
)

