#-*-coding:utf-8-*-
import hashlib
import re
from tornado import locale
import torngas.utils.strtools as strtools
# 验证是否email
def is_email(self, email=''):
    if not hasattr(self, 'email_pattern'):
        self.email_pattern = re.compile(r'^([\w]+)(\.[\w]+)*@([\w\-]+\.){1,5}([A-Za-z]){2,4}$')
    match = self.email_pattern.match(email)
    return True if match else False

    # 对密码进行hash加密


def get_hashMD5(self, pwd_string=''):
    mdhash = hashlib.md5(pwd_string)
    md5string = mdhash.hexdigest()
    sort = "bXZ/gDAbQA+zaTxdqJwxKa8OZTbuZE/ok3doaow9N4Q="
    md5string_hash = hashlib.md5(md5string + sort)

    return md5string_hash.hexdigest()


# 属性构造器
def xproperty(fget, fset, fdel=None, doc=None):
    if isinstance(fget, str):
        attr_name = fget

        def fget(obj):
            return getattr(obj, attr_name)

    elif isinstance(fset, str):
        attr_name = fset

        def fset(obj, val):
            setattr(obj, attr_name, val)
    else:
        raise TypeError, 'either fget or fset must be a str'

    return property(fget, fset, fdel, doc)

# 判断中英文字节长度，1中文=2英文
def get_wordcount(string, local_code='zh_CN'):
    ustr = strtools.safeunicode(string)
    if local_code == 'zh_CN':
        return len(ustr.encode('gbk'))/2

if __name__ == "__main__":
    print get_wordcount('我')
    print ' 的   　　    '.strip(),'s'
    print 's'