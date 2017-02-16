#!/usr/bin/env python3
import re
import datetime
import requests

from parse import get_rates


def main():
    session = requests.Session()
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    issuer = 'Spar Nord Bank'
    rates_mc, t1 = get_rates(session, date_str, issuer=issuer,
                             card='MasterCard', cache_time=True)
    rates_visa, t2 = get_rates(session, date_str, issuer='',
                               card='VISA', cache_time=True)
    t = min(t1, t2)
    with open('today.tpl.html') as fp:
        tpl = fp.read()

    currencies = {
        'MasterCard': dict(rates_mc)['USD'],
        'VISA': dict(rates_visa)['USD'],
    }

    greatest = max(currencies, key=currencies.__getitem__)
    least = min(currencies, key=currencies.__getitem__)
    ratio = float(currencies[greatest]) / float(currencies[least])
    percentage = '%.2f' % (100 * ratio)

    data = dict(
        issuer=issuer,
        date=date_str,
        mc=currencies['MasterCard'],
        visa=currencies['VISA'],
        retrieved=t.strftime('%Y-%m-%d %H:%M:%S'),
        greatest=greatest,
        least=least,
        percentage=percentage,
    )

    def repl(mo):
        return str(data[mo.group(1)])

    output = re.sub(r'\{\{ ([a-z]+) \}\}', repl, tpl)

    with open('today.html', 'w') as fp:
        fp.write(output)


if __name__ == '__main__':
    main()
