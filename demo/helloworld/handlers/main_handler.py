
from torngas.handler import WebHandler
from torngas import settings
from torngas.logger import access_logger,trace_logger,info_logger,SysLogger
class BaseHandler(WebHandler):
    """
    do some your base things
    """
    pass


class Main(BaseHandler):
    def get(self):
        welcome = "Hello,Torngas!"
        self.finish(self._url_kwargs['abc'])
        # self.render("index.html", welcome=welcome)
