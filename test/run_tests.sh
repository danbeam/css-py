#!/bin/bash

TESTDIR=$(dirname `readlink $0`);
ROOTDIR=$(dirname $TESTDIR);

assertEqual() {
  if [ "$1" != "$2" ]; then
    echo "Assertion failed:" >&2;
    echo "$1 vs $2";
    exit 1;
  fi
}

lextest=$(python $ROOTDIR/css/csslex.py $TESTDIR/lexer/test-all.css | cut -d',' -f1 | cut -d '(' -f2 | grep '^[A-Z]' | sort | uniq -c);
assertEqual "$lextest" "`cat $TESTDIR/lexer/test-all.expected.txt`";

for dir in `/bin/ls "$TESTDIR" | grep -v '^lexer'`; do
  
done;
