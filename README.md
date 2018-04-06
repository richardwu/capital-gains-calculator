# Capital Gains Calculator

Need to calculate the [adjusted cost base
(ACB)](https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-127-capital-gains/calculating-reporting-your-capital-gains-losses/adjusted-cost-base.html)
of your sell transactions for reporting capital gains on your Canadian tax
return?

## How-to

Simply run with `python capital-gains.py` (requires Python 3+) and follow the
interactive command line (type `?` for list of commands).

## Examples

Entering new transaction
```
> new
Enter the security's symbol (e.g. BTC): btc
New security. Please enter a description (optional): Bitcoin
Enter transaction date (MM-DD-YYYY): 02-20-2017
Transaction type (buy/sell): buy
Enter quantity: 40
Enter average price per share: 2500
Enter fees (default: 0):

New "BTC" transaction summary:
Date: Feb 20, 2017
Type: buy
Quantity: 40
Price per share: 2500
Fee: 0.0

Add transaction? (y/n): y
Updated BTC with transaction.
```

Viewing all transactions
```
> list
List of all securities and transactions:
BTC - Bitcoin
mm-dd-yyyy      type    quantity           price             fee
02-20-2017       buy          40            2500               0
03-15-2017       buy          20            5000               0
04-20-2017      sell          15            7000               0
05-12-2017       buy          12            2000              10
07-02-2017      sell          13           13370               2
ETH - Ethereum
mm-dd-yyyy      type    quantity           price             fee
03-17-2017       buy          50           400.5               5
03-20-2017      sell          25             450               0
```

Calculate adjusted cost base (ACB) for sell transactions
```
> acb
List of symbols:
BTC
ETH

Specify the symbol to calculate ACB for sell transactions: btc
ACB for BTC:
mm-dd-yyyy      type    quantity           price             fee             ACB        gain/loss
02-20-2017       buy          40            2500               0
03-15-2017       buy          20            5000               0
04-20-2017      sell          15            7000               0        50000.00        55000.00
05-12-2017       buy          12            2000              10
07-02-2017      sell          13           13370               2        39686.49        134121.51
Remaining quantity: 44
Remaining ACB: 134323.5087719298245614035088
```

Saving transactions to a save file
```
> save
File to save to: top-secret-crypto.cgc
Save to top-secret-crypto.cgc successful.
```

Loading transactions from a save file
```
> load
File to load from: top-secret-crypto.cgc
Loading from top-secret-crypto.cgc will erase all current data. Are you sure? (y/n): y
Load from top-secret-crypto.cgc complete.
List of all securities and transactions:
BTC - Bitcoin
mm-dd-yyyy      type    quantity           price             fee
02-20-2017       buy          40            2500               0
03-15-2017       buy          20            5000               0
04-20-2017      sell          15            7000               0
05-12-2017       buy          12            2000              10
07-02-2017      sell          13           13370               2
ETH - Ethereum
mm-dd-yyyy      type    quantity           price             fee
03-17-2017       buy          50           400.5               5
03-20-2017      sell          25             450               0
```

## Outstanding items

- FIFO/LIFO methods
- Editing/deleting transactions (currently must edit save file directly)
- Error handling when invalid input for values
