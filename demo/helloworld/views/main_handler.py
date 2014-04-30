from torngas.handlers import WebHandler
from torngas.cache import get_cache


class BaseHandler(WebHandler):
    """
    do some your base things
    """
    pass


class Main(BaseHandler):
    def get(self):
        # cache = get_cache('')
        welcome = "Hello,Torngas!"
        self.render("index.html", welcome=welcome)
