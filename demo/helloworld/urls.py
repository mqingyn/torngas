# !/usr/bin/env python
# -*- coding: utf-8 -*-
from torngas.urlhelper import Url, route

u = Url('helloworld.views')
urls = route(
    u(name='Index', pattern=r'/', handler='main_handler.Main')
)

