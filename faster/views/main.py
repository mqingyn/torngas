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
import logging
import json
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.colors import *
from fabric.tasks import execute
from tornado import web, gen
from tornado.web import asynchronous
from tornado.util import import_object
from torngas.utils import Null
from fabric import network
from torngas.handlers.common_handler import WebHandler
from torngas.cache import get_cache
from torngas.decorators.async_execute import async_execute
from .. import SITE_SETTINGS
from torngas.inject_factory import factory

PROJECT_DEPLOY_KEY = "proj_deploy_%s_%s"


class Base(WebHandler):
    def static_url(self, path, include_host=None, **kwargs):
        self.require_setting("static_path", "static_url")
        get_url = self.settings.get("static_handler_class",
                                    web.StaticFileHandler).make_static_url

        if include_host is None:
            include_host = getattr(self, "include_host", False)

        if include_host:
            base = self.request.protocol + "://" + self.request.host
        else:
            base = ""

        version = self.site_settings.static_version
        return '%s?v=%s' % (base + get_url(self.settings, path, include_version=False, **kwargs), version)

    @property
    def site_settings(self):
        return SITE_SETTINGS

    def render(self, template_name, **kwargs):
        kwargs['site_settings'] = self.site_settings
        return super(Base, self).render(template_name, **kwargs)

    def check_xsrf_cookie(self):
        """
        重写xsrf适应angularjs
        """
        try:

            params = json.loads(self.request.body)
        except Exception:
            params = {}
        token = (self.get_argument("_xsrf", None) or
                 self.request.headers.get("X-Xsrftoken") or
                 self.request.headers.get("X-Csrftoken") or
                 params.get("_xsrf"))
        if not token:
            raise web.HTTPError(403, "'_xsrf' argument missing from POST")
        if self.xsrf_token != token:
            raise web.HTTPError(403, "XSRF cookie does not match POST argument")

    @property
    def cache(self):
        return get_cache("default")

from torngas.helpers.logger_helper import logger
class Index(Base):
    def on_prepare(self):
        pass

    def get(self, group_id=1):
        project_group = self.site_settings.projects
        groups = []
        projects = None
        for item in project_group:

            groups.append({"g_name": item['group_name'], "g_id": item['group_id']})
            if item['group_id'] == group_id:
                projects = item['project']

        kw = locals()
        kw.pop('self')

        self.render('faster/index.html', **kw)


class GetProject(Base):
    def get(self, group_id):
        project_group = self.site_settings.projects
        projects = None

        for item in project_group:
            if str(item['group_id']) == str(group_id):
                projects = item['project']

        if projects:
            for p in projects:
                status = self.cache.get(PROJECT_DEPLOY_KEY % (group_id, p['name']))
                p['is_succ'] = status['is_succ'] if status else 'na'
                p['msg'] = status['msg'] if status else 'N/A'
                p['ip'] =p['host'].split('@')[1]

        self.write({
            'is_succ': True,
            'projects': projects
        })


class Deploy(Base):
    @gen.coroutine
    def post(self):
        params = json.loads(self.request.body)
        group_id = params.get('group_id', 0)
        proj_name = params.get('proj_name', '')
        if not group_id or not proj_name:
            self.write({"is_succ": False, "msg": "depoly faliure"})
        cache_key = PROJECT_DEPLOY_KEY % (group_id, proj_name)
        self.cache.set(cache_key, dict(is_succ='ing', msg='正在发布...'), 3600 * 24)
        result = yield gen.Task(self.deploy, group=group_id, proj_name=proj_name)

        self.cache.set(cache_key, dict(is_succ=result[0], msg=result[1]), 3600 * 24)
        self.finish({"is_succ": result[0], "msg": result[1]})


    @async_execute
    def deploy(self, group=None, proj_name=None, callback=None):
        project_group = self.site_settings.projects
        project = None

        for item in project_group:
            if str(item['group_id']) == str(group):
                for proj in item['project']:
                    if proj['name'] == proj_name:
                        project = proj
                        break
        if project:
            env.hosts, env.password = [project['host']], str(project['ssh_pwd'])
            is_local, root_dir = project['local'], project['root_dir']
            (run_cd, go) = (lcd, local) if is_local else (cd, run)

            def command():
                with run_cd(root_dir):
                    with settings(warn_only=True):
                        go('supervisorctl stop %s' % proj_name)
                    with run_cd(proj_name):
                        go('git status')
                        go('git pull origin master')
                        with settings(warn_only=True):
                            go('supervisorctl start %s' % proj_name)

            try:
                result = execute(command, hosts=env.hosts)
                network.disconnect_all()
                return True, result
            except BaseException, ex:
                return False, ex.message
        else:
            return False, "no project"


if __name__ == '__main__':
    pass