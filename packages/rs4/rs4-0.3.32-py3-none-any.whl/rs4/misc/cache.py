from functools import wraps, _make_key
import time
import threading
import math
from datetime import datetime as dt, timedelta

class _HashedSeq(list):
    __slots__ = 'hashvalue'
    def __init__(self, tup, hash=hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue

def _make_key (args, kwds, typed = False, kwd_mark = (object(),), fasttypes = {int, str}, tuple=tuple, type=type, len=len):
    key = args
    if kwds:
        key += kwd_mark
        for item in kwds.items():
            key += item
    if typed:
        key += tuple(type(v) for v in args)
        if kwds:
            key += tuple(type(v) for v in kwds.values())
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)

class datetime:
    @staticmethod
    def get_next_minute (date, minutes = 10):
        # 10 minutes caching: 4 - > 9, 42 -> 49
        tick = -1
        while 1:
            tick = min (59, tick + minutes)
            if tick >= date.minute:
                break
        return dt.strptime (
            "{}{:02d}".format (date.strftime ("%Y%m%d%H"), tick), "%Y%m%d%H%M"
        ).astimezone (date.tzinfo)

    @staticmethod
    def get_next_hour (date, hours = 1):
        return dt.strptime (
            (date + timedelta (hours = hours)).strftime ("%Y%m%d%H"), "%Y%m%d%H"
        ).astimezone (date.tzinfo)

class KeyCache:
    def __init__ (self, maxsize = 256, expires = 0):
        self.maxsize = maxsize
        self.expires = expires
        self._cache = {}
        self._keys = []
        self._lock = threading.Lock ()

    def __len__ (self):
        with self._lock:
            return len (self._cache)

    def get (self, key):
        with self._lock:
            if len (self._cache) > self.maxsize:
                self._cache.pop (self._keys.pop (0))
            try:
                cached, y = self._cache [key]
            except KeyError:
                return None

        if not self.expires or cached + self.expires > int (time.time ()):
            return y

        with self._lock:
            self._cache.pop (self._keys.pop (self._keys.index (key)))
        return None

    def put (self, key, val):
        if key is None:
            return
        with self._lock:
            if key in self._cache:
                return
            self._cache [key] = (int (time.time ()), val)
            self._keys.append (key)


CACHES = {}

def fifo_cache (maxsize, expires = 0):
    def decorator(f):
        global CACHES
        if f not in CACHES:
            CACHES [f] = KeyCache (maxsize, expires)

        @wraps (f)
        def wrapper (*args, **kwargs):
            global CACHES
            cache_key = _make_key (args, kwargs)
            y = CACHES [f].get (cache_key)

            if y:
                return y
            y = f (*args, **kwargs)
            CACHES [f].put (cache_key, y)
            return y
        return wrapper
    return decorator

def key_cache (maxsize, expires = 0):
    def decorator(f):
        global CACHES
        if f not in CACHES:
            CACHES [f] = KeyCache (maxsize, expires)

        @wraps (f)
        def wrapper (cache_key, *args, **kwargs):
            global CACHES
            if cache_key:
                y = CACHES [f].get (cache_key)
                if y:
                    return y
            y = f (cache_key, *args, **kwargs)
            CACHES [f].put (cache_key, y)
            return y
        return wrapper
    return decorator

