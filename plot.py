import json
import datetime
from decimal import Decimal

import matplotlib.pyplot as plt


def main():
    input = {}
    with open('rates-mc.json') as fp:
        input['MasterCard'] = json.load(fp)
    with open('rates-visa.json') as fp:
        input['VISA'] = json.load(fp)
    symbol = 'USD'
    for source, all_data in input.items():
        data = all_data[symbol]
        xs = [datetime.datetime.strptime(key, '%Y-%m-%d')
              for key in data.keys()]
        ys = [Decimal(value) for value in data.values()]
        plt.plot(xs, ys, label=source)
    plt.legend(loc='upper left')
    plt.show()


if __name__ == '__main__':
    main()
