#!/usr/bin/env python3
import json
import datetime
from decimal import Decimal

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from caching import rates_cache


@rates_cache
def get_rates(date, issuer, card, session=None):
    raise StopIteration


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
    date = get_latest_date(date, [issuer], [card])
    while True:
        yield date, get_rates(date.strftime('%Y-%m-%d'), issuer, card)
        date -= datetime.timedelta(days=1)


def main():
    today = datetime.date.today()
    input = {
        'MasterCard': past_rates_from(today, 'Spar Nord Bank', 'MasterCard'),
        'VISA': past_rates_from(today, '', 'VISA'),
    }
    symbol = 'USD'
    for source, all_data in input.items():
        xs, ys = [], []
        for date, rates in all_data:
            rate = next(r for s, r in rates if s == symbol)
            xs.append(date)
            ys.append(Decimal(rate))
        plt.plot(xs, ys, label=source)
    plt.legend(loc='upper left')
    plt.gca().format_xdata = lambda d: mdates.num2date(d).strftime('%Y-%m-%d')
    plt.show()


if __name__ == '__main__':
    main()
