#!/usr/bin/python3
"""
A simple class to represent a Quicken (QIF) file, and a parser to
load a QIF file into a sequence of those classes.

It's enough to be useful for writing conversions.
"""

import sys
 
class QifItem:
    def __init__(self):
        #self.order = ['date', 'amount', 'cleared', 'num', 'payee', 'memo', 'address', 'category', 'categoryInSplit', 'memoInSplit', 'amountOfSplit']
        self.order = ['date', 'amount', 'payee']
        self.date = None
        self.amount = None
        #self.cleared = None
        #self.num = None
        self.payee = None
        #self.memo = None
        #self.address = None
        #self.category = None
        #self.categoryInSplit = None
        #self.memoInSplit = None
        #self.amountOfSplit = None

    def show(self):
        pass
    '''
    def __repr__(self):
        titles = ','.join(self.order)
        tmpstring = ','.join( [str(self.__dict__[field]) for field in self.order] )
        tmpstring = tmpstring.replace('None', '')
        return titles + "," + tmpstring
    '''
    def __repr__(self):
        return "<QifItem date:%s amount:%s payee:%s>" % (self.date, self.amount, self.payee)

    def dataString(self):
        """
        Returns the data of this QIF without a header row
        """
        tmpstring = ','.join( [str(self.__dict__[field]) for field in self.order] )
        tmpstring = tmpstring.replace('None', '')
        return tmpstring

def parseQif(infile):
    """
    Parse a qif file and return a list of entries.
    infile should be open file-like object (supporting readline() ).
    """

    items = []
    curItem = QifItem()
    line = infile.readline()
    while line != '':
        if line[0] == '\n': # blank line
            pass
        elif line[0] == '^': # end of item
            # save the item
            items.append(curItem.date)
            items.append(curItem.amount)
            items.append(curItem.payee)
            items.append('^')
            items = '\n'.join(items)
            print(items)
            #print(repr(curItem))
            del curItem
            curItem = QifItem()
            #print(repr(curItem))
            items = []
        elif line[0] == 'D':
            curItem.date = line[0] + line[1:-1]
        elif line[0] == 'T':
            curItem.amount = line[0] + line[1:-1]
        #elif line[0] == 'N':
        #    curItem.num = line[1:-1]
        #elif line[0] == 'C':
        #    curItem.cleared = line[1:-1]
        elif line[0] == 'P':
            curItem.payee = line[0] + line[1:-1]
        elif line[0] == 'M':
            curItem.memo = line[1:-1]
        #elif line[0] == 'A':
        #    curItem.address = line[1:-1]
        elif line[0] == 'L':
            curItem.category = line[1:-1]
        elif line[0] == 'S':
            try:
                curItem.categoryInSplit.append(";" + line[1:-1])
            except AttributeError:
                curItem.categoryInSplit = line[1:-1]
        elif line[0] == 'E':
            try:
                curItem.memoInSplit.append(";" + line[1:-1])
            except AttributeError:
                curItem.memoInSplit = line[1:-1]
        elif line[0] == '$':
            try:
                curItem.amountInSplit.append(";" + line[1:-1])
            except AttributeError:
                curItem.amountInSplit = line[1:-1]
        #else:
            # don't recognise this line; ignore it
            #print(f"Skipping unknown line: {line}")
            
        '''
        print(f"curItem.date = {curItem.date}")
        print(f"curItem.amount = {curItem.amount}")
        print(f"curItem.payee = {curItem.payee}")
        '''
        line = infile.readline()
    return items


if __name__ == "__main__":
    # read from stdin and write CSV to stdout
    items = parseQif(sys.stdin)
    #print(repr(items[0]))
    #for item in items[1:]:
    #    print(item.dataString())
