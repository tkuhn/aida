#!/bin/bash
#
# Usage:
# $ scripts/make-rdf.sh
#

enc="$(perl -MURI::Escape -e 'print uri_escape($ARGV[0]);' -- "$6")"
enc=`echo "$enc" | sed s/%20/+/g`

echo "AIDA-URI" \
  > temp-aida-uris.txt

cat tables/all.csv \
  | egrep -v '^SOURCE,' \
  | sed -r 's/^([^,]*),([^,]*),\"(.*)\",([^,]*),([^,]*)$/\3/' \
  | scripts/make-aida-uri.sh \
  >> temp-aida-uris.txt

paste -d ',' tables/all.csv temp-aida-uris.txt \
  > temp-table.csv

cat temp-table.csv \
  | egrep -v '^SOURCE,' \
  | sed -r 's_^([^,]*),([^,]*),\"(.*)\",([^,]*),([^,]*),([^,]*)$_<\1> <http://purl.org/petapico/o/hycl#\2> <\6>_' \
  > rdf/data.nt

rm temp-aida-uris.txt
rm temp-table.csv
