#!/bin/sh

echo "Running pre-commit tests...";
for f in `/bin/ls ./css/*_unittest.py`; do
  output=$(python $f);
  if [ $? -ne 0 ]; then
    echo "$output" >&2;
    exit 1
  fi
done;

exit 0
