#-*-coding=utf8-*-
from torngas.helpers.route_helper import url, RouteLoader

route = RouteLoader(path_prefix='Main.views', path='/', app_folder='Main')

urls = route.urlhelper(
    url('Index', r'/', 'view=main_handler,handler=Main')
)
