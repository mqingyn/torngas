#!/usr/bin/env python
# -*- coding: utf-8 -*-
from torngas.urlhelper import Url

u = Url('helloworld.views')
urls = u.route(
    u(name='Index', pattern=r'/', handler='main_handler.Main')
)

