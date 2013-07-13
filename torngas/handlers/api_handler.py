#-*-coding=utf8-*-
import json
from torngas.exception import APIError
from common_handler import CommonHandler


class ApiHandler(CommonHandler):
    def get_format(self):
        format = self.get_argument('format', None)
        if not format:
            accept = self.request.headers.get('Accept')
            if accept:
                if 'javascript' in accept:
                    format = 'jsonp'
                else:
                    format = 'json'
        return format or 'json'


    def write_api(self, obj, nofail=False):
        format = self.get_format()
        if format == 'json':
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(json.dumps(obj))
        elif format == 'jsonp':
            self.set_header("Content-Type", "application/javascript")
            callback = self.get_argument('callback', 'callback')
            self.write('%s(%s);' % (callback, json.dumps(obj)))
        elif nofail:
            self.write(json.dumps(obj))
        else:
            raise APIError(400, 'Unknown response format requested: %s' % format)

            #根据场景可实现个性化的api错误处理
            # def write_error(self, status_code, **kwargs):
            #     errortext = 'Internal error'
            #     error_code = status_code
            #     import traceback
            #
            #     self.logger.error(traceback.format_exc())
            #     if kwargs.get('error_code'):
            #         error_code = kwargs.get('error_code')
            #     exc_info = kwargs.get('exc_info')
            #     if exc_info:
            #         errortext = getattr(exc_info[1], 'log_message', errortext)
            #     self.write_api({'error_code': error_code,
            #                     'error_info': errortext,
            #                     'description': self.request.path},
            #                    nofail=True)
