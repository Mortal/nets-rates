import os
import json
import pickle
import inspect
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
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            cache_key = {k: bound_args.arguments[k] for k in key}
            cache_key_str = json.dumps(cache_key, sort_keys=True)
            try:
                return cache[cache_key_str]
            except KeyError:
                cache[cache_key_str] = fn(*args, **kwargs)
                with open(tmp_filename, 'w' + mode) as fp:
                    module.dump(cache, fp)
                os.rename(tmp_filename, cache_filename)
                return cache[cache_key_str]

        return wrapped

    return decorator


rates_cache = cache(
    'rates-cache.pkl', 'rates-cache.tmp', ('date', 'issuer', 'card'))
