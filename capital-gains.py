from __future__ import division

import dateutil.parser
import os
import sys
from functools import total_ordering

from decimal import Decimal

securities = {}

def yesno_input(msg):
    action = None
    while not action == 'y' and not action == 'n':
        if action is not None:
            print('Invalid action. Please try again.')
        action = input(msg)

    return action

@total_ordering
class Security:
    @total_ordering
    class Transaction:
        # This must corespond to the number of variables per transaction below.
        NUM_VARS = 5

        def __init__(self, date, typ, quantity, priceper, fee):
            self.date = date
            self.typ = typ
            self.quantity = Decimal(quantity)
            self.priceper = Decimal(priceper)
            self.fee = Decimal(fee)

        def __str__(self):
            return '{}\t{:>4}\t{:>8}\t{:>8}\t{:>8}'.format(self.datestr(), self.typ, self.quantity, self.priceper, self.fee)

        def __lt__(self, other):
            return self.date < other.date or (self.date == other.date and self.typ < other.typ)

        def __eq__(self, other):
            return self.date == other.date and self.typ == other.typ

        def datestr(self):
            return self.date.strftime('%m-%d-%Y')

        def serialize(self):
            return '{},{},{},{},{}'.format(self.datestr(), self.typ, self.quantity, self.priceper, self.fee)

        @classmethod
        def deserialize(cls, csv):
            fields = csv.split(',')
            assert(len(fields) == cls.NUM_VARS)
            return cls(dateutil.parser.parse(fields[0]), fields[1], Decimal(fields[2]), Decimal(fields[3]), Decimal(fields[4]))

        @classmethod
        def header(cls):
            return 'mm-dd-yyyy\t{:>4}\t{:>8}\t{:>8}\t{:>8}'.format('type', 'quantity', 'price', 'fee')

    def __init__(self, sym, desc):
        self.sym = sym
        self.desc = desc
        self.trans = []

    def __str__(self):
        out = self.sym
        if self.desc:
            out = '{} - {}'.format(out, self.desc)
        return out

    def __lt__(self, other):
        return self.sym < other.sym

    def __eq__(self, other):
        return self.sym == other.sym

    def toLongStr(self):
        out = '{}'.format(self)
        if self.trans:
            out = '{}\n{}\n{}'.format(out, self.Transaction.header(), '\n'.join([str(tran) for tran in sorted(self.trans)]))
        return out

    def add_tran(self, tran):
        self.trans.append(tran)

    def serialize(self):
        return '{},{},{}'.format(self.sym, self.desc, ','.join([tran.serialize() for tran in sorted(self.trans)]))

    @classmethod
    def deserialize(cls, csv):
        fields = csv.split(',')
        assert(len(fields) >= 3)
        sec = Security(fields[0], fields[1])
        # No transactions.
        if len(fields) == 3:
            return sec

        # Parse transactions..
        trans_csv = fields[2:]
        assert(len(trans_csv) % cls.Transaction.NUM_VARS == 0)
        for i in range(0, len(trans_csv), cls.Transaction.NUM_VARS):
            sec.add_tran(cls.Transaction.deserialize(','.join(trans_csv[i:i+cls.Transaction.NUM_VARS])))

        return sec


def new_security(sym = None):
    if sym is None:
        sym = input('Enter the security\'s symbol (e.g. BTC): ')

    if sym in securities:
        print('Error: {} already exists.'.format(sym))
        return

    desc = input('New security. Please enter a description (optional): ')
    securities[sym] = Security(sym, desc)

def command_new():
    sym = input('Enter the security\'s symbol (e.g. BTC): ').upper()
    if sym not in securities:
        new_security(sym)

    security = securities[sym]
    assert(security.sym == sym)

    date = None
    while date is None:
        try:
            date = dateutil.parser.parse(input('Enter transaction date (MM-DD-YYYY): '))
        except ValueError as e:
            print('Could not parse date: {} Please try again.'.format(str(e)))
    typ = None
    while not typ == 'buy' and not typ == 'sell':
        if typ is not None:
            print('Invalid action. Please try again.')
        typ = input('Transaction type (buy/sell): ')
    quantity = Decimal(input('Enter quantity: '))
    price = Decimal(input('Enter average price per share: '))
    fee = input('Enter fees (default: 0): ')
    if fee == '':
        fee = 0.0
    else:
        fee = Decimal(fee)

    print(
            '\nNew "{}" transaction summary:\nDate: {}\nType: {}\nQuantity: {}\nPrice per share: {}\nFee: {}\n'.format(
                sym,
                date.strftime('%b %d, %Y'),
                typ,
                quantity,
                price,
                fee
            )
        )

    if yesno_input('Add transaction? (y/n): ') == 'y':
        security.add_tran(Security.Transaction(date, typ, quantity, price, fee))
        print('Updated {} with transaction.'.format(sym))
    else:
        print('Did not add new transaction.'.format(sym))

    return

def command_list():
    if not securities:
        print('No securities entered yet.')
        return

    print('List of all securities and transactions:')
    print('\n'.join([security.toLongStr() for _, security in sorted(securities.items())]))

def command_desc(fn):
    if fn == command_help:
        return 'Show valid commands.'
    elif fn == command_new:
        return 'Add a new transaction'
    elif fn == command_acb:
        return 'Print adjusted cost base (ACB) for transactions.'
    elif fn == command_list:
        return 'List all securities and transactions.'
    elif fn == command_load:
        return 'Load transactions from a dump file.'
    elif fn == command_save:
        return 'Save all transactions to a dump file.'
    elif fn == command_exit:
        return 'Exit the program.'
    else:
        print(fn)
        raise BaseException('invalid function command.')


def command_help():
    print('\n'.join(['{}:\t{}'.format(cmd, command_desc(fn)) for (cmd, fn) in sorted(command_tbl.items())]))

def command_acb():
    print('List of symbols:\n{}\n'.format('\n'.join([sym for sym in securities.keys()])))

    sym = None
    while sym is None or sym not in securities:
        if sym is not None:
            print('{} does not exist. Please try again.'.format(sym))
        sym = input('Specify the symbol to calculate ACB for sell transactions: ').upper()

    sec = securities[sym]

    print('ACB for {}:'.format(sym))
    print('{}\t{:>8}\t{:>8}'.format(Security.Transaction.header(), 'ACB', 'gain/loss'))
    # Running quantity and ACB.
    quant = Decimal(0)
    acb = Decimal(0)
    for tran in sorted(sec.trans):
        tran_out = str(tran)
        if tran.typ == 'buy':
            quant += tran.quantity
            acb += tran.quantity * tran.priceper + tran.fee
        else:
            if(quant < tran.quantity):
                print('Warning: sell transaction occurred for {} shares on {} when only {} shares available.'.format(tran.quantity, tran.datestr(), quant))
            # Calculate ACB and gain/loss of sell transaction.
            acb_sell = acb * tran.quantity / quant
            gainloss = (tran.quantity * tran.priceper) - acb_sell - tran.fee
            tran_out = '{}\t{:>8}\t{:>8}'.format(tran_out, round(acb_sell, 2), round(gainloss, 2))

            quant -= tran.quantity
            acb -= acb_sell
        print(tran_out)

    print('Remaining quantity:', quant)
    print('Remaining ACB:', acb)

def command_load():
    fpath = None
    while fpath is None or not os.path.exists(fpath):
        if fpath is not None:
            print('File {} does not exist. Please try again.'.format(fpath))
        fpath = input('File to load from: ')

    if yesno_input('Loading from {} will erase all current data. Are you sure? (y/n): '.format(fpath))  == 'n':
        return

    global securities
    securities = {}
    with open(fpath, 'r') as fd:
        for line in fd:
            sec = Security.deserialize(line)
            securities[sec.sym] = sec

    print('Load from {} complete.'.format(fpath))
    command_list()

def command_save():
    fpath = None
    while fpath is None or os.path.exists(fpath):
        if fpath is not None:
            if yesno_input('File {} already exists. Overwrite? (y/n): '.format(fpath)) == 'y':
                break
        fpath = input('File to save to: ')

    with open(fpath, 'w') as fd:
        fd.write('\n'.join([sec.serialize() for sec in securities.values()]))
    print('Save to {} successful.'.format(fpath))

def command_exit():
    if yesno_input('Save before exiting? (y/n): ') == 'y':
        command_save()
    sys.exit(0)

command_tbl = {
        '?': command_help,
        'help': command_help,
        'n': command_new,
        'new': command_new,
        'acb': command_acb,
        'l': command_list,
        'list': command_list,
        'load': command_load,
        's': command_save,
        'save': command_save,
        'e': command_exit,
        'exit': command_exit,
        }

if __name__ == '__main__':
    print('Welcome to Capital Gains Calculator. Type ? for a list of commands.')
    while True:
        command = input('> ').strip()

        if command not in command_tbl:
            print('Invalid input "{}". Type ? for help.'.format(command))
            continue

        command_tbl[command]()
