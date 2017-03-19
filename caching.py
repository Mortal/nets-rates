import os
import json
import pickle
import inspect
import datetime
import functools


TIME_SUFFIX = '_time'


def cache(cache_filename, tmp_filename, key):
    def decorator(fn):
        signature = inspect.signature(fn)
        date_fmt = '%Y-%m-%d %H:%M:%S.%f'

        def parse(args, kwargs):
            return_cache_time = kwargs.pop('cache_time', False)
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            cache_key = {k: bound_args.arguments[k] for k in key}
            cache_key_str = json.dumps(cache_key, sort_keys=True)
            return cache_key_str, return_cache_time

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            cache_key_str, return_cache_time = parse(args, kwargs)
            date_key_str = cache_key_str + TIME_SUFFIX
            try:
                res = decorator.cache[cache_key_str]
            except KeyError:
                res = decorator.cache[cache_key_str] = fn(*args, **kwargs)
                cache_time = datetime.datetime.now()
                decorator.cache[date_key_str] = cache_time.strftime(date_fmt)
                save()
            else:
                try:
                    cache_time = datetime.datetime.strptime(
                        decorator.cache[date_key_str], date_fmt)
                except KeyError:
                    cache_time = None
                    if return_cache_time:
                        print("Warning: No cache time stored for %s" %
                              cache_key_str)
            if return_cache_time:
                return res, cache_time
            else:
                return res

        def delete(*args, **kwargs):
            cache_key_str, return_cache_time = parse(args, kwargs)
            del decorator.cache[cache_key_str]
            try:
                return datetime.datetime.strptime(
                    decorator.cache.pop(cache_key_str + TIME_SUFFIX), date_fmt)
            except KeyError:
                pass

        def save():
            print("Saving %s" % cache_filename)
            with open(tmp_filename, 'w' + mode) as fp:
                module.dump(decorator.cache, fp)
            os.rename(tmp_filename, cache_filename)

        wrapped.delete = delete
        wrapped.save = save

        return wrapped

    base, ext = os.path.splitext(cache_filename)
    module, mode = {'.pkl': (pickle, 'b'), '.json': (json, '')}[ext]
    try:
        with open(cache_filename, 'r' + mode) as fp:
            decorator.cache = module.load(fp)
        print("Loaded %s" % cache_filename)
    except FileNotFoundError:
        decorator.cache = {}
        if module is pickle:
            try:
                with open(base + '.json') as fp:
                    decorator.cache = json.load(fp)
                print("Loaded old %s" % (base + '.json'))
            except FileNotFoundError:
                pass

    dummy_fn = eval('lambda %s: 0' % ', '.join(key), {}, {})
    dummy_sig = inspect.signature(dummy_fn)

    def get_key(*args, **kwargs):
        bound_args = signature.bind(*args, **kwargs)
        cache_key = {k: bound_args.arguments[k] for k in key}
        cache_key_str = json.dumps(cache_key, sort_keys=True)
        return cache_key_str

    def parse_key(key_str):
        if key_str.endswith(TIME_SUFFIX):
            key_str = key_str[:-len(TIME_SUFFIX)]
        key_dict = json.loads(key_str)
        assert isinstance(key_dict, dict)
        assert set(key_dict.keys()) == set(key)
        return tuple(key_dict[k] for k in key)

    decorator.get_key = get_key
    decorator.parse_key = parse_key
    decorator.keys = lambda: map(parse_key, decorator.cache.keys())

    return decorator


rates_cache = cache(
    'rates-cache.pkl', 'rates-cache.tmp', ('date', 'issuer', 'card'))
