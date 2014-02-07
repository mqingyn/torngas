import threading, base64, hashlib

from tornado.ioloop import PeriodicCallback
from torngas.utils.storage import sorteddict

_MAX_CAPACITY = 500
_RECYCLING_CAPACITY = 100


class ContainerManager(object):
    _object_instance = sorteddict()

    def __init__(self, lifecycle=False):
        if lifecycle:
            PeriodicCallback(self.lifecycle, 3600 * 1000).start()

    def get(self, item, *args, **kwargs):

        name = '.'.join([item.__module__, item.__name__])
        inst_name = hashlib.sha1(base64.b64encode(':'.join([name, repr(args) + repr(kwargs)])))
        inst_name = inst_name.hexdigest()

        if name in self._object_instance and inst_name in self._object_instance[name]:
            item = self._object_instance.pop(name)#
            self._object_instance[name] = item
            return item[inst_name]
        else:

            if name in self._object_instance:
                item = self._object_instance.pop(name)#
                self._object_instance[name] = item
            else:
                self._object_instance[name] = dict()
            if inst_name not in self._object_instance[name]:
                self._object_instance[name][inst_name] = item(*args, **kwargs)
        return self._object_instance[name][inst_name]


    def lifecycle(self):
        if len(self._object_instance) >= _MAX_CAPACITY:
            for index in range(_RECYCLING_CAPACITY - 1, -1, -1):
                key = self._object_instance.keys()[index]
                del self._object_instance[key]


container = ContainerManager(True)




