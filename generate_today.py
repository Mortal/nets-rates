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
    print('<p>Date: %s</p>' % date_str)
    print('<p>MasterCard: %s</p>' % (dict(rates_mc)['USD'],))
    print('<p>VISA: %s</p>' % (dict(rates_visa)['USD'],))
    print('<p>Data retrieved: %s</p>' % (t,))


if __name__ == '__main__':
    main()
