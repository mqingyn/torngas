# -*-coding=utf8-*-
from torngas.helpers.route_helper import url, RouteLoader

route = RouteLoader(path='/')

urls = route.urlhelper('Main.views',
    url('Index', r'/', 'main_handler.Main')
)

if __name__ == '__main__':
    pass
