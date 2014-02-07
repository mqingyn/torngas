from torngas.utils import lazyimport
from torngas.utils.storage import storage


def importall( path=()):
    module_dict = dict()

    module_list = map(lazyimport, path)
    for l in module_list:
        module_dict[l.__name__.split('.')[-1]] = l

    return storage(module_dict)