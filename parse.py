import datetime
import urllib.parse

import html5lib
import requests


NS = dict(h='http://www.w3.org/1999/xhtml')


def get_doc(session, date, issuer='Spar Nord Bank', card='MasterCard'):
    assert card in ('MasterCard', 'VISA')
    try:
        with open('output.html') as fp:
            return html5lib.parse(fp.read())
    except FileNotFoundError:
        pass
    base = 'https://miscweb.nets.eu/exchangerates/getRates'
    params = dict(newDate=date.strftime('%m/%d/%Y'), issuerInstId='',
                  language='en', cardOrg=card, issuer=issuer)
    r = session.get(base, params=params)
    return html5lib.parse(r.content, transport_encoding=r.encoding)


def get_table_contents(table_element):
    thead = table_element.find('h:thead', NS)
    print(thead)


def main():
    session = requests.Session()
    date = datetime.date.today()
    doc = get_doc(session, date)
    table = doc.find('.//*[@id="ratesTable"]', NS)
    print(table)
    print(get_table_contents(table))


if __name__ == '__main__':
    main()
