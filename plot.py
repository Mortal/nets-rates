#!/usr/bin/env python3
import argparse
import datetime
from decimal import Decimal

from caching import rates_cache
from generate_today import get_config


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


def past_rates_from(date, issuer, card, days=float('inf')):
    date = get_latest_date(date, [issuer], [card])
    i = 0
    while i < days:
        i += 1
        yield date, get_rates(date.strftime('%Y-%m-%d'), issuer, card)
        date -= datetime.timedelta(days=1)


def get_data(date, days):
    currency, issuer_mc, issuer_visa = get_config(
        'currency, issuer_mc, issuer_visa')
    input = {
        'MasterCard': past_rates_from(date, issuer_mc, 'MasterCard',
                                      days),
        'VISA': past_rates_from(date, issuer_visa, 'VISA', days),
    }
    for source, all_data in input.items():
        xs, ys = [], []
        for date, rates in all_data:
            rate = next(r for s, r in rates if s == currency)
            xs.append(date)
            ys.append(Decimal(rate))
        yield xs, ys, source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o')
    parser.add_argument('--days', '-d', type=int, default=float('inf'))
    args = parser.parse_args()

    if args.output:
        import matplotlib
        matplotlib.use('Agg')

    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    today = datetime.date.today()

    days = 0
    for xs, ys, source in get_data(today, args.days):
        days = max(days, len(xs))
        plt.plot(xs, ys, label=source)
    plt.legend(loc='upper left')

    if days > 1000:
        major = mdates.YearLocator()
        minor = mdates.MonthLocator()
        label = mdates.DateFormatter('%Y')
    elif days > 365:
        major = mdates.MonthLocator()
        minor = mdates.DayLocator()
        label = mdates.DateFormatter('%b %Y')
    elif days > 30:
        major = mdates.MonthLocator()
        minor = mdates.DayLocator()
        label = mdates.DateFormatter('%b %e')
    else:
        major = minor = mdates.DayLocator()
        label = mdates.DateFormatter('%b %e')

    plt.gca().xaxis.set_major_locator(major)
    plt.gca().xaxis.set_minor_locator(minor)
    plt.gca().xaxis.set_major_formatter(label)
    plt.grid()

    if args.output:
        plt.savefig(args.output)
    else:
        # Change format of data in status bar on mouseover
        plt.gca().format_xdata = (
            lambda d: mdates.num2date(d).strftime('%Y-%m-%d'))
        plt.show()


if __name__ == '__main__':
    main()
