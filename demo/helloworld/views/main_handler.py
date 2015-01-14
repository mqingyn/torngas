
from torngas.handler import WebHandler
from torngas import settings
class BaseHandler(WebHandler):
    """
    do some your base things
    """
    pass


class Main(BaseHandler):
    def get(self):
        welcome = "Hello,Torngas!"
        self.render("index.html", welcome=welcome)
