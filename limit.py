from functools import wraps


class LimiterMiXin(object):

    def __init__(self, key_index=""):
        self.key_index = "limiter_"+key_index

    """
    limits : "max(number)/time(second)", 0 means no limit.
    example: "10/60", 10 count per minute.
    """
    def limit(self, key_func=None, limit_format="0/0", callback=None):
        def func_wrapper(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not callable(key_func):
                    return func(*args, **kwargs)
                if not callable(callback):
                    return func(*args, **kwargs)
                try:
                    key = str(key_func())
                except:
                    return func(*args, **kwargs)

                if key == "":
                    return func(*args, **kwargs)

                if self._filter("%s_%s" % (self.key_index, key), limit_format):
                    return callback()

                return func(*args, **kwargs)

            return wrapper

        return func_wrapper

    def _filter(self, key, limit_format):
        count, timeout = self._format(limit_format)
        if count == 0:
            return False
        current_count = self.get_count(key)
        if not current_count:
            self.create_count(key, timeout)
            return False
        if current_count <= count:
            self.incr_count(key, timeout)
            return False
        if current_count > count:
            self.incr_count(key, timeout)
            return True
        return True

    def _format(self, limit_format):
        format_list = limit_format.split("/")
        if len(format_list) != 2:
            return 0, 0
        try:
            count = int(format_list[0])
            timeout = int(format_list[1])
            return count, timeout
        except:
            return 0, 0

    def create_count(self, *args, **kwargs):
        pass

    def get_count(self, *args, **kwargs):
        return 0

    def incr_count(self, *args, **kwargs):
        return 0

    def set_black(self):
        pass


class LimiterRedis(LimiterMiXin):

    def __init__(self, redis=None, key_index=""):
        self.db = redis
        super(LimiterRedis, self).__init__(key_index)

    def create_count(self, key, timeout):
        return self.db.setex(key, 1, timeout)

    def get_count(self, key):
        try:
            count = self.db.get(key)
            if not count:
                return count
            return int(count)
        except:
            return 0

    def incr_count(self, key, timeout):
        try:
            count = self.db.incr(key)
        except:
            return
        if count <= 1:
            """
            If count is 0, it does not exist before, so we need to set the timeout
            """
            self.db.expire(key, timeout)




