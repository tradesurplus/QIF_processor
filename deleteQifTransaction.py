#!/usr/bin/python3

import argparse
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


def deleteqiftran(infile):
    """
    Parse a qif file and return a list of entries.
    infile should be open file-like object (supporting readline() ).
    """

    transitems = []
    curitem = QifItem()
    line = infile.readline()
    while line != '':
        if line[0] == '\n':  # blank line
            pass
        elif line[0] == '^':  # end of item
            # save the item
            if curitem.date is not None:
                transitems.append(curitem.date)
            if curitem.memo is not None:
                transitems.append(curitem.memo)
            if curitem.amount is not None:
                transitems.append(curitem.amount)
            if curitem.payee is not None:
                transitems.append(curitem.payee)
            if curitem.category is not None:
                transitems.append(curitem.category)
            if curitem.date is not None:
                transitems.append('^')
            transitems = '\n'.join(transitems)
            print(transitems)
            del curitem
            curitem = QifItem()
            transitems = []
        elif line[0] == 'D':
            curitem.date = line[0] + line[1:-1]
        elif line[0] == 'T':
            curitem.amount = line[0] + line[1:-1]
        elif line[0] == 'N':
            curitem.num = line[1:-1]
        # elif line[0] == 'C':
        #    curitem.cleared = line[1:-1]
        #
        # Preprocessing the payee name isn't necessary because
        # KMyMoney has builtin tools to handle name matching
        elif line[0] == 'P':
            if re.search('tfr-', line[1:-1]):
                transref, tfrfmaccount, tfrtoaccount = parseibline('transfer', line[1:-1])
                # search tfrfmaccount and tfrtoaccount for the value passed via '-a' or '--account'
                tfraccount = args.account
                if tfraccount == tfrfmaccount or tfraccount == tfrtoaccount:
                    # print(f"Current line: {line[1:-1]}")
                    # print(f"tfraccount: {tfraccount}, tfrfmaccount: {tfrfmaccount}, tfrtoaccount: {tfrtoaccount}")
                    curitem.date = None
                    curitem.amount = None
                    curitem.payee = None
                # if re.search('9088', tfrfmaccount):
                #     curitem.category = 'L[Current Assets:NAB iSaver 9088]'
                #     curitem.payee = 'PTransfer'
                # elif re.search('8134', tfrfmaccount):
                #     curitem.category = 'L[Current Assets:NAB Cash Manager 8134]'
                #     curitem.payee = 'PTransfer'
                # elif re.search('6150', tfrtoaccount):
                #     curitem.category = 'L[Current Assets:NAB Classic Banking (cheque) 6150]'
                #     curitem.payee = 'PTransfer'
                # if re.search('6150', tfrtoaccount):
                #     curitem.category = 'L[Current Assets:NAB Classic Banking (cheque) 6150]'
                #     curitem.payee = 'PTransfer'
                # elif re.search('8134', tfrtoaccount):
                #     curitem.category = 'L[Current Assets:NAB Cash Manager 8134]'
                #     curitem.payee = 'PTransfer'
                # elif re.search('3215', tfrtoaccount):
                #     curitem.category = 'L[Current Assets:NAB Cash Manager 3215]'
                #     curitem.payee = 'PTransfer'
                # elif re.search('9088', tfrtoaccount):
                #     curitem.category = 'L[Current Assets:NAB iSaver 9088]'
                #     curitem.payee = 'PTransfer'
                else:
                    curitem.payee = line[0] + line[1:-1]
            else:
                curitem.payee = line[0] + line[1:-1]
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


if __name__ == "__main__":
    # read from stdin and write amended QIF to stdout
    qifparser = argparse.ArgumentParser(description='Get transaction identifier')
    qifparser.add_argument('-a', '--account', type=str, metavar='', help='Specify which transaction to delete')
    args = qifparser.parse_args()

    deleteqiftran(sys.stdin)
