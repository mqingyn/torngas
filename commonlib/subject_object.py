from torngas import Null
from commonlib.utilib import xproperty
from torngas.utils.storage import storage


class SubjectObject(object):
    _subject_object_code = Null()
    _subject_object_result = Null()
    _subject_object_ext = Null()

    def __init__(self, code, obj):
        self._subject_object_result = obj
        self._subject_object_code = code

    @property
    def c(self):
        return self._subject_object_code
    @property
    def r(self):
        return self._subject_object_result

    def _set_ext(self, ext):
        self._subject_object_ext = ext

    ext = xproperty('_subject_object_ext', _set_ext)


so = SubjectObject

so_code = storage(dict(
    ok=1000,
    data_exist=1001,
    data_no_exist=1002,
    authorized_failure=1003,
    argument_invalid=1004,
    unknown_error=5001,
))