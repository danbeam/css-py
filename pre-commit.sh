#!/bin/sh

for f in `/bin/ls ./css/*_unittest.py`; do
  python $f || exit $?
done;

exit 0
