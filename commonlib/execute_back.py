from torngas.utils import Null
from commonlib.utilib import xproperty
from torngas.utils.storage import storage


class ExecuteBack(object):
    _execute_status_code = Null()
    _execute_object_result = Null()
    _execute_object_ext = Null()

    def __init__(self, status_code, execute_result):
        self._execute_object_result = execute_result
        self._execute_status_code = status_code

    @property
    def c(self):
        return self._execute_status_code

    @property
    def er(self):
        return self._execute_object_result

    def _set_ext(self, ext):
        self._execute_object_ext = ext

    ext = xproperty('_execute_object_ext', _set_ext)


# eb = ExecuteBack
class StatusCode(object):
    ok = 2000,
    file_err = 4001,
    qiniu_err = 4002,
    unknown_err = 5000


StatusCode = StatusCode()