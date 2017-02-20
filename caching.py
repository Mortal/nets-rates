import os
import json
import pickle
import inspect
import datetime
import functools


def cache(cache_filename, tmp_filename, key):
    base, ext = os.path.splitext(cache_filename)
    module, mode = {'.pkl': (pickle, 'b'), '.json': (json, '')}[ext]
    try:
        with open(cache_filename, 'r' + mode) as fp:
            cache = module.load(fp)
        print("Loaded %s" % cache_filename)
    except FileNotFoundError:
        cache = {}
        if module is pickle:
            try:
                with open(base + '.json') as fp:
                    cache = json.load(fp)
                print("Loaded old %s" % (base + '.json'))
            except FileNotFoundError:
                pass

    def decorator(fn):
        signature = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            return_cache_time = kwargs.pop('cache_time', False)
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            cache_key = {k: bound_args.arguments[k] for k in key}
            cache_key_str = json.dumps(cache_key, sort_keys=True)
            date_key_str = cache_key_str + '_time'
            date_fmt = '%Y-%m-%d %H:%M:%S.%f'
            try:
                res = cache[cache_key_str]
            except KeyError:
                res = cache[cache_key_str] = fn(*args, **kwargs)
                cache_time = datetime.datetime.now()
                cache[date_key_str] = cache_time.strftime(date_fmt)
                with open(tmp_filename, 'w' + mode) as fp:
                    module.dump(cache, fp)
                os.rename(tmp_filename, cache_filename)
            else:
                try:
                    cache_time = datetime.datetime.strptime(
                        cache[date_key_str], date_fmt)
                except KeyError:
                    cache_time = None
                    if return_cache_time:
                        print("Warning: No cache time stored for %s" %
                              cache_key_str)
            if return_cache_time:
                return res, cache_time
            else:
                return res

        def recompute(*args, **kwargs):

        return wrapped

    return decorator


rates_cache = cache(
    'rates-cache.pkl', 'rates-cache.tmp', ('date', 'issuer', 'card'))
