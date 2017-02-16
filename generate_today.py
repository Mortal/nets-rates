#!/usr/bin/env python3
import os
import re
import datetime
import requests

from parse import get_rates, get_url


DEFAULT_CONFIG = [
    ('currency', 'USD'),
    ('issuer_mc', 'Spar Nord Bank'),
    ('issuer_visa', ''),
]


def get_config(*keys):
    if len(keys) == 1:
        keys = keys[0].replace(',', ' ').split()
    assert set(keys) <= set(k for k, v in DEFAULT_CONFIG)
    try:
        import config
    except ImportError:
        base = os.path.dirname(__file__)
        config_path = os.path.join(base, 'config.py')
        print("Generating %s..." % config_path)
        with open(config_path, 'x') as fp:
            for k, v in DEFAULT_CONFIG:
                fp.write('%s = %r\n' % (k, v))
        import config
    missing = [k for k in keys if not hasattr(config, k)]
    if missing:
        default_dict = dict(DEFAULT_CONFIG)
        defaults = ', '.join('%s = %r' % (k, default_dict[k]) for k in missing)
        raise Exception('config.py should define %s' % defaults)
    return tuple(getattr(config, k) for k in keys)


def main():
    currency, issuer_mc, issuer_visa = get_config(
        'currency, issuer_mc, issuer_visa')
    session = requests.Session()
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    issuer = 'Spar Nord Bank'
    rates_mc, t1 = get_rates(session, date_str, issuer=issuer_mc,
                             card='MasterCard', cache_time=True)
    url_mc = get_url(date=now, issuer=issuer_mc, card='MasterCard')
    rates_visa, t2 = get_rates(session, date_str, issuer=issuer_visa,
                               card='VISA', cache_time=True)
    url_visa = get_url(date=now, issuer=issuer_visa, card='VISA')

    t = min(t1, t2)
    with open('today.tpl.html') as fp:
        tpl = fp.read()

    currencies = {
        'MasterCard': dict(rates_mc)[currency],
        'VISA': dict(rates_visa)[currency],
    }

    greatest = max(currencies, key=currencies.__getitem__)
    least = min(currencies, key=currencies.__getitem__)
    ratio = float(currencies[greatest]) / float(currencies[least])
    percentage = '%.2f' % (100 * ratio)

    data = dict(
        currency=currency,
        issuer=issuer_mc or issuer_visa,
        date=date_str,
        mc=currencies['MasterCard'],
        visa=currencies['VISA'],
        url_mc=url_mc,
        url_visa=url_visa,
        retrieved=t.strftime('%Y-%m-%d %H:%M:%S'),
        greatest=greatest,
        least=least,
        percentage=percentage,
    )

    def repl(mo):
        return str(data[mo.group(1)])

    output = re.sub(r'\{\{ ([a-z_]+) \}\}', repl, tpl)

    with open('today.html', 'w') as fp:
        fp.write(output)


if __name__ == '__main__':
    main()
