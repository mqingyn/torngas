#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2013,掌阅科技
All rights reserved.

摘    要：
创 建 者：mengqingyun
创建日期：2014-1-24
"""
import os
import sys
from commonlib.site_settings import SiteSettings
import service.test
import service.test2
sys.path.append('.')
SITE_SETTINGS = SiteSettings(os.path.dirname(__file__))
SUBAPP_NAME = 'faster'

if __name__ == '__main__':

    print os.path.abspath('.')