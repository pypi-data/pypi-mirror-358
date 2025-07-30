import functools


class cached_property:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        functools.update_wrapper(self, func)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        if not hasattr(instance, "_cache"):
            raise AttributeError("Instance must have a '_cache' attribute")

        cache = instance._cache
        if self.name not in cache:
            cache[self.name] = self.func(instance)
        return cache[self.name]


def clears_cache(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, "_cache"):
            self._cache.clear()
        return func(self, *args, **kwargs)
    return wrapper


class PropertyCache(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"No cached value for {name!r}")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"No cached value named {name!r}")


class PropertyCacheMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._cache = PropertyCache()
