# -*-coding=utf8-*-
from torngas.helpers.route_helper import url, RouteLoader
from . import SUBAPP_NAME
route = RouteLoader(path='/', subapp_name=SUBAPP_NAME)

urls = route.urlhelper(
    url('Index', r'/', 'views.main.Index')
)

if __name__ == '__main__':
    pass