#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by 'mengqingyun' on 15/1/17.

# import all model for syncdb
from models.main_models import *

from torngas.db.dbalchemy import Connector


def syncdb():
    for k, conn in Connector.conn_pool.items():
        conn.create_db()