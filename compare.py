import json
import datetime
from decimal import Decimal

import matplotlib.pyplot as plt

from caching import cache


@cache('rates-cache.pkl', 'rates-cache.tmp', ('date', 'issuer', 'card'))
def get_rates(date, issuer, card, session=None):
    raise StopIteration
    # assert card in ('MasterCard', 'VISA')
    # date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
    # doc = get_doc(session, date_obj, issuer=issuer, card=card)
    # table = doc.find('.//*[@id="ratesTable"]', NS)
    # header, rows = get_table_contents(table)
    # currency = header.index('Currency')
    # rate = header.index('Exchange rate')
    # rates = [(row[currency], row[rate]) for row in rows]
    # return rates


def get_latest_date(date, issuers, cards):
    for _ in range(100):
        try:
            for i, c in zip(issuers, cards):
                get_rates(date.strftime('%Y-%m-%d'), i, c)
        except StopIteration:
            date -= datetime.timedelta(days=1)
            continue
        else:
            return date


def past_rates_from(date, issuer, card):
    while True:
        yield date, get_rates(date.strftime('%Y-%m-%d'), issuer, card)
        date -= datetime.timedelta(days=1)


def past_ratio_from(date, symbol='USD'):
    date = get_latest_date(
        date, ('', 'Spar Nord Bank'), 'VISA MasterCard'.split())
    if not date:
        raise Exception("No data found")
    a = past_rates_from(date, '', 'VISA')
    b = past_rates_from(date, 'Spar Nord Bank', 'MasterCard')
    for (d, x), (d_, y) in zip(a, b):
        assert d == d_
        x_rate = next(r for s, r in x if s == symbol)
        y_rate = next(r for s, r in y if s == symbol)
        yield d, Decimal(x_rate) / Decimal(y_rate)


def main():
    dates, ratios = zip(*past_ratio_from(datetime.date.today()))
    plt.figure()
    plt.plot(dates, ratios)
    plt.figure()
    plt.plot(sorted(ratios))
    plt.show()


if __name__ == '__main__':
    main()
