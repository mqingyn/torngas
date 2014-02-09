#coding=utf8
try:
    import cPickle as pickle
except ImportError:
    import pickle
from torngas.cache.backends.rediscache import RedisCache


class RedisQueue(RedisCache):
    def get_listlenth(self, key, version=None):
        """
        获取列表长度
        """
        key = self.make_key(key, version=version)
        return self._client.llen(key)

    def delete_rem(self, key, count, value, version=None):
        """
        删除count个值为value的元素
        """
        key = self.make_key(key, version=version)
        return self._client.lrem(key, value, count)

    def delete_ltrim(self, key, start, stop, version=None):
        """
        删除仅保留区间内的元素
        """

        key = self.make_key(key, version=version)
        return self._client.ltrim(key, start, stop)

    def push(self, key, value, is_left=False, version=None):
        """
        从队列的右边入队一个元素
        """

        self.pushmany(key, [value], is_left, version)

    def pushmany(self, key, values=None, is_left=False, version=None):
        """
        从队列的右边入队多个元素
        """
        if not values: values = []

        vlist = [self._topickle(v) for v in values]

        key = self.make_key(key, version=version)

        if is_left:
            return self._client.lpush(key, *vlist)
        return self._client.rpush(key, *vlist)

    def pop(self, key, is_left=False, version=None):
        """
        从队列弹出一个元素
        """

        key = self.make_key(key, version=version)
        if is_left:
            result = self._client.lpop(key)
        else:
            result = self._client.rpop(key)
        value = self._tounpickle(result)
        return value

    def rpoppush(self, key1, key2, version=None):
        """
        取出列表1尾部的值并插入到列表2
        """
        key1 = self.make_key(key1, version=version)
        key2 = self.make_key(key2, version=version)

        return self._client.rpoplpush(key1, key2)

    def _topickle(self, value):

        if value and not isinstance(value, int) and not isinstance(value, bool):
            return pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        return value

    def _tounpickle(self, value):


        if value and not isinstance(value, int) and not isinstance(value, bool):
            return pickle.loads(value)
        return value

    def setlist_value(self, key, index, value, version=None):
        """
        设置指定索引的值
        """
        key = self.make_key(key, version=version)

        return self._client.lset(key, index, self._topickle(value))

    def getindex_value(self, key, index, version=None):
        """
        获取指定索引下的值
        """
        key = self.make_key(key, version=version)
        return self._tounpickle(self._client.lindex(key, index))

    def getrange(self, key, start, end, version=None):
        """
        获取指定区间内的值列表
        """
        key = self.make_key(key, version=version)

        result_list = self._client.lrange(key, start, end)

        return [self._tounpickle(v) for v in result_list]

    #
    # 集合部分
    def set_addone(self, key, member=None, version=None):
        """
        向集合添加一个或多个值
        """
        if not member:
            return
        return self.set_add(key, [member], version=version)

    def set_add(self, key, members=None, version=None):
        """
        向集合添加一个或多个值
        """
        if not members: members = []
        key = self.make_key(key, version=version)
        vlist = [self._topickle(v) for v in members]
        return self._client.sadd(key, *vlist)


    def set_pop(self, key, version=None):
        """
        从集合弹出随机元素并返回
        """
        key = self.make_key(key, version=version)

        return self._tounpickle(self._client.spop(key))

    def set_popnodel(self, key, version=None):
        """
        返回集合的随机元素但不删除
        """
        key = self.make_key(key, version=version)
        return self._tounpickle(self._client.srandmember(key))

    def set_removeone(self, key, value=None, version=None):
        """
        删除集合内一个
        """
        if not values: return
        return self.set_remove(key, [value], version=version)

    def set_remove(self, key, values=None, version=None):
        """
        删除集合内多个值
        """
        if not values: values = []
        key = self.make_key(key, version=version)
        vlist = [self._topickle(v) for v in values]

        return self._client.srem(key, *vlist)

    def set_getmembers(self, key, version=None):
        """
        返回集合的所有元素
        """
        key = self.make_key(key, version=version)
        return [self._tounpickle(v) for v in self._client.smembers(key)]