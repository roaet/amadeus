#!/bin/bash

dir="$1/amadeus"
echo "Searching: $dir"

count=`find $dir ! -name "runner.py" -name "*.py" -type f -exec \
    grep "ipdb" '{}' \; -print | \
    grep ipdb | awk '{$1=$1};1' | \
    grep "^import" | wc -l | awk '{$1=$1};1'`
if [ "$count" -eq "0" ]; then
    exit 0;
fi
echo "Found $count instances of uncommented ipdb ignoring runner.py"
echo "Locations:"
find $dir ! -name "runner.py" -name "*.py" -type f -exec \
    grep -n "ipdb" '{}' \; -print
exit 1
