from torngas.handlers import WebHandler


class BaseHandler(WebHandler):
    """
    do some your base things
    """


class Main(BaseHandler):
    def get(self):
        welcome = "hello word!"
        self.render("index.html", welcome=welcome)
