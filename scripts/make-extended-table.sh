#!/bin/bash
#
# Usage:
# $ scripts/make-extended-table.sh
#

echo "AIDA-URI" \
  > temp-aida-uris.txt

cat tables/all.csv \
  | egrep -v '^SOURCE,' \
  | sed -r 's/^([^,]*),([^,]*),\"(.*)\",([^,]*),([^,]*)$/\3/' \
  | scripts/make-aida-uri.sh \
  >> temp-aida-uris.txt

paste -d ',' tables/all.csv temp-aida-uris.txt \
  > tables/all-extended.csv

rm temp-aida-uris.txt
