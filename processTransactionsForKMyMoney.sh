#!/bin/bash

# command line instructions to emulate:
# sed 's/\r$//' QIF_TransactionHistory_test_file.qif | ./parseQif.py > test.qif; sed -i '1s;^;!Type:Bank\n;' test.qif

EXEDIR="/home/john/SpiderOak\ Hive/SpiderOak/dev/KMyMoney/"
export processedTime=`date '+%Y%m%d_%H%M%S'`

usage() {
        print "Usage: $0 [-i inputfile]"
        print "  -i  QIF export from online banking"
}

while getopts ":i:" opt; do
    case $opt in
                i) inputfile=$OPTARG;;
                h|*) usage; exit 1;;
    esac
done
shift $(($OPTIND - 1))

eval cd ${EXEDIR}

sed 's/\r$//' ${inputfile} | ./parseQif.py > parsed${processedTime}${inputfile}
sed -i '1s;^;!Type:Bank\n;' parsed${processedTime}${inputfile}
