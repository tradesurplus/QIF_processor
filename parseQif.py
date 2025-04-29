#!/usr/bin/python3
"""
A simple class to represent a Quicken (QIF) file, and a parser to
load a QIF file into a sequence of those classes.

It's enough to be useful for writing conversions.
"""

import argparse
from datetime import datetime
import re
import sys


class QifItem:
    def __init__(self):
        # self.order = ['date', 'amount', 'cleared', 'num', 'payee', 'memo', 'address', 'category',
        # 'categoryInSplit', 'memoInSplit', 'amountOfSplit']
        self.order = ['date', 'amount', 'payee', 'memo', 'category']
        self.date = None
        self.amount = None
        # self.cleared = None
        # self.num = None
        self.payee = None
        self.memo = None
        # self.address = None
        self.category = None
        # self.categoryInSplit = None
        # self.memoInSplit = None
        # self.amountOfSplit = None

    """
    def __repr__(self):
        return "<QifItem date:%s amount:%s payee:%s>" % (self.date, self.amount, self.payee)
    """

def main() -> None:
    # read from stdin and write amended QIF to stdout
    parseqif(sys.stdin)

def parse_args():
    qifparser = argparse.ArgumentParser(description='Get transaction identifier')
    qifparser.add_argument('-a', '--account', type=str, metavar='', help='The account from which transactions have been extracted.')
    args = qifparser.parse_args()
    return args

def parseqif(infile):
    """
    Parse a qif file and return a list of entries.
    infile should be open file-like object (supporting readline() ).
    """

    # dictionary of currently used accounts
    accounts = {
        '3215':'Current Assets:NAB Cash Manager 3215',
        '6150':'Current Assets:NAB Classic Banking (cheque) 6150',
        '8134':'Current Assets:NAB Cash Manager 8134',
        '9088':'Current Assets:NAB iSaver 9088'
    }
    transitems = []
    curitem = QifItem()
    line = infile.readline()
    while line != '':
        if line[0] == '\n':  # blank line
            pass
        elif line[0] == '^':  # end of item
            # save the item
            transitems.append(curitem.date)
            if curitem.memo is not None:
                transitems.append(curitem.memo)
            transitems.append(curitem.amount)
            transitems.append(curitem.payee)
            if curitem.category is not None:
                transitems.append(curitem.category)
            transitems.append('^')
            transitems = '\n'.join(transitems)
            print(transitems)
            del curitem
            curitem = QifItem()
            transitems = []
        elif line[0] == 'D':
            converteddate = datetime.strptime(line[1:-1], '%d/%m/%y').strftime('%Y-%m-%d')
            curitem.date = line[0] + converteddate
            #curitem.date = line[0] + line[1:-1]
        elif line[0] == 'T':
            curitem.amount = line[0] + line[1:-1]
        # elif line[0] == 'N':
        #    curitem.num = line[1:-1]
        # elif line[0] == 'C':
        #    curitem.cleared = line[1:-1]
        #
        # Preprocessing the payee name isn't necessary because
        # KMyMoney has builtin tools to handle name matching
        elif line[0] == 'P':
            if re.search('tfr-', line[1:-1]):
                transref, tfrfmaccount, tfrtoaccount = parseibline('transfer', line[1:-1])
                # search tfrfmaccount and tfrtoaccount for the value passed via '-a' or '--account'
                cmdlineargs = parse_args()
                tfraccount = cmdlineargs.account
                curitem.memo = 'MRef:  ' + transref
                if tfraccount == tfrfmaccount:
                    curitem.category = 'L[' + accounts[tfrtoaccount] + ']'
                elif tfraccount == tfrtoaccount:
                    curitem.category = 'L[' + accounts[tfrfmaccount] + ']'
                curitem.payee = 'PTransfer'
            elif re.search('^BPAY', line[1:-1]):
                transref, tranpayee = parseibline('bpay', line[1:-1])
                curitem.memo = 'MRef:  ' + transref
                # curitem.payee = 'P' + tranpayee
                curitem.payee = line[0] + line[1:-1]
            elif re.search('^MOOSE', line[1:-1]):
                transref = parseibline('moose', line[1:-1])
                curitem.memo = 'MRef:  ' + transref
                # curitem.payee = 'P' + tranpayee
                curitem.payee = line[0] + line[1:-1]
            elif re.search('OCSP', line[1:-1]):
                transref = parseibline('ocsp', line[1:-1])
                curitem.memo = 'MRef:  ' + transref
                # curitem.payee = 'P' + tranpayee
                curitem.payee = line[0] + line[1:-1]
            else:
                curitem.payee = line[0] + parsepayeeline(line[1:-1])
                catval = lookupcategory(parsepayeeline(line[1:-1]))
                if catval is not None:
                    curitem.category = 'L' + catval
        elif line[0] == 'M':
            curitem.memo = line[1:-1]
        # elif line[0] == 'A':
        #    curitem.address = line[1:-1]
        elif line[0] == 'L':
            curitem.category = line[1:-1]
        elif line[0] == 'S':
            try:
                curitem.categoryInSplit.append(";" + line[1:-1])
            except AttributeError:
                curitem.categoryInSplit = line[1:-1]
        elif line[0] == 'E':
            try:
                curitem.memoInSplit.append(";" + line[1:-1])
            except AttributeError:
                curitem.memoInSplit = line[1:-1]
        elif line[0] == '$':
            try:
                curitem.amountInSplit.append(";" + line[1:-1])
            except AttributeError:
                curitem.amountInSplit = line[1:-1]
        # else:
            # don't recognise this line; ignore it
            # print(f"Skipping unknown line: {line}")
        line = infile.readline()
    return transitems


def lookupcategory(payee):
    """
    Lookup the category a payee transaction is assigned to.
    """
    categorydict = {
        # 'tfr-9088': '[Current Assets:NAB iSaver 9088]',
        'NAB':'Interest Income:Savings Interest',
        'ORIGINgas':'Utilities:Gas',
        'ORIGINelectric':'Utilities:Electric'
    }
    # category = categorydict.get(payee, 'Uncategorised')
    category = categorydict.get(payee)
    return category


def parsepayeeline(payeelinefrombank):
    """
    Parse the payee line from the bank QIF
    file to extract a simplified customer name.
    :param payeelinefrombank:
    :return:
    """

    """
    KMyMoney can match transactions to payee using a matching function
    attached to the payee properties so this my not be necessary for
    simple transaction/payee matches.
    """
    if re.search('INTEREST|null', payeelinefrombank):
        payeename = 'NAB'
    elif re.search('300006206027', payeelinefrombank):
        payeename = 'ORIGINgas'
    elif re.search('300001204225', payeelinefrombank):
        payeename = 'ORIGINelectric'
    else:
        # print(f"Can't find customer {payeelinefrombank}")
        payeename = payeelinefrombank
    return payeename


def parseibline(trantype, ibline):
    # Extract details from an internet banking transaction to use in other fields
    if trantype == 'transfer':
        # transcomponents = re.search('(ONLINE) (.*) (tfr-[0-9]{4})to([0-9]{4})(.*)', ibline)
        transcomponents = re.search('(ONLINE) (.*) tfr-([0-9]{4})to([0-9]{4})(.*)', ibline)
        transref = transcomponents.group(2)  # this goes in the M field
        tfrfmaccount = transcomponents.group(3)  # this goes in the L field
        tfrtoaccount = transcomponents.group(4)
        # print(f"tfrfmaccount {transcomponents.group(3)}")
        # print(f"tfrtoaccount {transcomponents.group(4)}")
        return transref, tfrfmaccount, tfrtoaccount

    if trantype == 'bpay':
        transcomponents = re.search('BPAY (.{11}) (.*)', ibline)
        transref = transcomponents.group(1)
        tranpayee = transcomponents.group(2)
        return transref, tranpayee
    
    if trantype == 'moose':
        transcomponents = re.search(r'MOOSE MOBILE\s+(.{11}).*', ibline)
        transref = transcomponents.group(1)
        return transref
    
    if trantype == 'ocsp':
        transcomponents = re.search(r'.*OCSP029234K (.{11}).*', ibline)
        transref = transcomponents.group(1)
        return transref


if __name__ == "__main__":
    main()
