#!/usr/bin/env python3
import json
import argparse
import datetime

import html5lib
import requests

from caching import rates_cache


NS = dict(h='http://www.w3.org/1999/xhtml')


# @cache('http-cache.json', 'http-cache.tmp', ('url', 'params'))
def http_get(session, url, params):
    print('Retrieving {url} {params}'.format(url=url, params=params))
    response = session.get(url, params=params)
    try:
        text = response.content.decode('utf8')
    except UnicodeDecodeError:
        return dict(bytes=response.content.encode('latin1'),
                    encoding=response.encoding)
    else:
        return dict(text=text)


def parse_cached(session, url, params):
    result = http_get(session, url, params)
    if 'text' in result:
        return html5lib.parse(result['text'])
    else:
        return html5lib.parse(result['bytes'].decode('latin1'),
                              transport_encoding=result['encoding'])


def get_url_data(date, issuer, card):
    base = 'https://miscweb.nets.eu/exchangerates/getRates'
    params = dict(newDate=date.strftime('%m/%d/%Y'), issuerInstId='',
                  language='en', cardOrg=card, issuer=issuer)
    return base, params


def get_url(date, issuer, card):
    base, params = get_url_data(date, issuer, card)
    return '%s?%s#ratesTable' % (base, requests.compat.urlencode(params))


def get_doc(session, date, issuer, card):
    base, params = get_url_data(date, issuer, card)
    return parse_cached(session, base, params)


def get_table_contents(table_element):
    header_row, = table_element.findall('h:thead/h:tr', NS)
    header = [c.text.strip() for c in header_row]
    rows = table_element.findall('h:tbody/h:tr', NS)
    row_contents = [
        [c.text.strip() for c in row]
        for row in rows]
    return header, row_contents


def previous_weekday(date):
    MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
    wd = date.weekday()
    if wd in (MON, SAT, SUN):
        subtract = (wd - FRI) % 7
    else:
        subtract = 1
    res = date - datetime.timedelta(days=subtract)
    assert MON <= res.weekday() <= FRI
    assert 1 <= (date - res).days <= 3
    return res


def previous_weekday_str(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    res = previous_weekday(date)
    return date.strftime('%Y-%m-%d')


@rates_cache
def get_rates(session, date, issuer, card, validate_today=False):
    assert card in ('MasterCard', 'VISA')
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
    doc = get_doc(session, date_obj, issuer=issuer, card=card)
    table = doc.find('.//*[@id="ratesTable"]', NS)
    header, rows = get_table_contents(table)
    currency = header.index('Currency')
    rate = header.index('Exchange rate')
    rates = [(row[currency], row[rate]) for row in rows]
    if validate_today:
        prev = previous_weekday_str(date)
        prev_rates = get_rates(session, prev, issuer, card)
        if prev_rates == rates:
            raise ValueError("No exchange rates for %s yet" % (date,))
        from pprint import pprint
        pprint([(r1, r2) for r1, r2 in zip(prev_rates, rates)
                if r1 != r2])
    return rates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', '-d', type=int, default=7)
    parser.add_argument('--recompute', '-r', type=int, default=0)
    args = parser.parse_args()

    session = requests.Session()
    today = datetime.date.today()
    result_mc = {}
    result_visa = {}
    for i in range(args.recompute):
        date = today - datetime.timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        t1 = get_rates.delete(
            session, date_str, issuer='Spar Nord Bank',
            card='MasterCard')
        t2 = get_rates.delete(session, date_str, issuer='', card='VISA')
        print(t1, t2)
    if args.recompute:
        get_rates.save()
    for i in range(args.days):
        date = today - datetime.timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        rates_mc = get_rates(session, date_str, issuer='Spar Nord Bank',
                             card='MasterCard')
        rates_visa = get_rates(session, date_str, issuer='',
                               card='VISA', validate_today=(i == 0))
        print(date, dict(rates_mc)['USD'], dict(rates_visa)['USD'])
        for symbol, rate in rates_mc:
            result_mc.setdefault(symbol, {})[date_str] = str(rate)
        for symbol, rate in rates_visa:
            result_visa.setdefault(symbol, {})[date_str] = str(rate)
    with open('rates-mc.json', 'w') as fp:
        json.dump(result_mc, fp, indent=2, sort_keys=True)
    with open('rates-visa.json', 'w') as fp:
        json.dump(result_visa, fp, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
