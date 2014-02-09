#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
摘    要：
创 建 者：mengqingyun
创建日期：2014-2-8
"""
import os
import sys
from commonlib.site_settings import SiteSettings
from torngas.inject_factory import factory, SINGLETON

sys.path.append('.')

from service.qiniu_service import QiniuService

factory.register('qiniu_srv', QiniuService, lifecycle_type=SINGLETON)
SITE_SETTINGS = SiteSettings(os.path.dirname(__file__))
SUBAPP_NAME = 'gipsy'

if __name__ == '__main__':
    print os.path.abspath('.')