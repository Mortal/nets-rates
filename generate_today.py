import re
import datetime
import requests

from parse import get_rates


def main():
    session = requests.Session()
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    rates_mc, t1 = get_rates(session, date_str, issuer='Spar Nord Bank',
                             card='MasterCard', cache_time=True)
    rates_visa, t2 = get_rates(session, date_str, issuer='', card='VISA',
                               cache_time=True)
    t = min(t1, t2)
    with open('today.tpl.html') as fp:
        tpl = fp.read()

    data = dict(
        date=date_str,
        mc=dict(rates_mc)['USD'],
        visa=dict(rates_visa)['USD'],
        retrieved=t,
    )

    def repl(mo):
        return str(data[mo.group(1)])

    output = re.sub(r'\{\{ ([a-z]+) \}\}', repl, tpl)

    with open('today.html', 'w') as fp:
        fp.write(output)


if __name__ == '__main__':
    main()
