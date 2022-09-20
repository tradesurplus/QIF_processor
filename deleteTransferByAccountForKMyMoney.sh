#!/bin/bash

# command line instructions to emulate:
# sed 's/\r$//' QIF_TransactionHistory_test_file.qif | ./deleteQifTransaction.py -a 3215 > zQIF_TransactionHistory_test_file.qif && sed -i '1s;^;!Type:Bank\n;' zQIF_TransactionHistory_test_file.qif && sed '/^$/d' zQIF_TransactionHistory_test_file.qif > zzQIF_TransactionHistory_test_file.qif

EXEDIR="/home/john/SpiderOak\ Hive/SpiderOak/dev/KMyMoney/"
export processedTime=`date '+%Y%m%d_%H%M%S'`

usage() {
        print "Usage: $0 [-a account -i inputfile]"
        print "  -a  transactions to remove by account number"
        print "  -i  QIF export from online banking. Don't use a preprocessed file; use a raw QIF export file then process it for KMyMoney."
}

while getopts ":a:i:" opt; do
    case $opt in
                a) account=$OPTARG;;
                i) inputfile=$OPTARG;;
                h|*) usage; exit 1;;
    esac
done
shift $(($OPTIND - 1))

eval cd ${EXEDIR}

sed 's/\r$//' ${inputfile} | ./deleteQifTransaction.py -a ${account} > parsed${processedTime}${inputfile}
sed -i '1s;^;!Type:Bank\n;' parsed${processedTime}${inputfile}
sed -i '/^$/d' parsed${processedTime}${inputfile}
