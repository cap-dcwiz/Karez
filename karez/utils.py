from functools import wraps
from inspect import isasyncgenfunction


def extract_dict(dic, *keys, **renames):
    d1 = {k: v for k, v in dic.items() if k in keys}
    d2 = {renames[k]: v for k, v in dic.items() if k in renames.keys()}
    return d1 | d2


def sync_generator_to_list(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return list(func(*args, **kwargs))

    return wrapper


def async_generator_to_list(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return [x async for x in func(*args, **kwargs)]

    return wrapper


def generator_to_list(func):
    if isasyncgenfunction(func):
        return async_generator_to_list(func)
    else:
        return sync_generator_to_list(func)
