from torngas.db.dbalchemy import sql_connection as sqlconn
from torngas.cache import get_cache
from torngas.helpers.settings_helper import settings
class BaseBackend(object):
    def __init__(self, *args, **kwargs):
        self.cache = get_cache(settings.BACKEND_CACHE_ALIAS)
        self.sqlconn = sqlconn.get_connetion
        self.initialize()


    def initialize(self):
        pass

