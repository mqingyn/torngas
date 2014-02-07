# -*-coding=utf8-*-
from torngas.helpers.route_helper import url, RouteLoader
from . import SUBAPP_NAME
route = RouteLoader(path='/', subapp_name=SUBAPP_NAME)

urls = route.urlhelper(
    url('Index', r'/', 'views.main.Index'),
    url('Panel',r'/panel/([0-9]+)','views.main.Index'),
    url('GetProject',r'/project/get/([0-9]+)','views.main.GetProject'),
    url('Deploy',r'/deploy','views.main.Deploy')
)

if __name__ == '__main__':
    pass