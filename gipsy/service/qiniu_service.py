#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import json
import base64
import urllib
import hashlib

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from commonlib.qiniusdk import conf, io, rs, fop, rpc
from commonlib.execute_back import ExecuteBack, StatusCode
from . import BaseService
from torngas.helpers.settings_helper import settings


class QiniuService(BaseService):
    def __init__(self):
        conf.ACCESS_KEY = settings.QINIU_ACCESSKEY
        conf.SECRET_KEY = settings.QINIU_SECRETKEY
        self.bucket = settings.QINIU_BUCKET[0]
        self.domain = settings.QINIU_DOMAIN


    def upload_imgfile(self, img_file, sizes):
        # import qiniu.io
        file_body = img_file['body']
        name = img_file['filename']
        name_splt = name.split(".")
        if len(name_splt) < 2:
            return ExecuteBack(StatusCode.file_err, None)

        save_name = "%s$%s" % (time.time(), name)
        save_name = hashlib.md5(base64.b64encode(save_name)).hexdigest()
        # save_name = "%s.%s" % (save_name, name_splt[1])

        policy = rs.PutPolicy('%s:%s' % (self.bucket, save_name))
        policy.returnBody = json.dumps({
            'hash': '$(etag)',
            'fname': '$(fname)',
            'key': '$(key)',
            'size': '$(fsize)',
            'w': '$(imageInfo.width)',
            'h': '$(imageInfo.height)',
            'mimeType': '$(mimeType)',
            'persistentId': '$(persistentId)',
            'format': '$(imageInfo.format)'
        })
        policy.insertOnly = 1

        def return_size_ops():
            ops = []
            for s in sizes:
                ops.append("imageView/2/w/%s/h/%s" % (s[0], s[1]))

            return ';'.join(ops)

        policy.persistentOps = return_size_ops()
        policy.persistentNotifyUrl = 'http://www.baidu.com'
        uptoken = policy.token()

        extra = io.PutExtra()
        extra.mime_type = "image/%s" % name[1].lower()
        data = StringIO.StringIO(file_body)
        ret, err = io.put(uptoken, save_name, data, extra)
        if err is not None:
            return ExecuteBack(StatusCode.qiniu_err, err)

        return ExecuteBack(StatusCode.ok, ret)


    def make_thumbnail(self, key, w, h, fmt='jpg'):
        """
        size = [(120,120),(320,240),(640,480),(1024,768)]
        mode = 1 # 1或2
        width = None # width 默认为0，表示不限定宽度
        height = None
        quality = None # 图片质量, 1-100
        format = None # 输出格式, jpg, gif, png, tif 等图片格式
	    """
        iv = fop.ImageView()
        iv.mode = 2
        iv.width = int(w)
        iv.height = int(h)
        key = rpc.encode_unicode(key)
        base_url = '/%s' % ( urllib.quote(key))
        req_url = iv.make_request(base_url)
        return req_url



