#!/bin/bash
#
# Usage:
# $ echo 'AIDA-SENTENCE' | scripts/make-aida-uri.sh
#

while read line; do
  enc="$(perl -MURI::Escape -e 'print uri_escape($ARGV[0]);' -- "$line")"
  echo "http://purl.org/aida/$enc" | sed s/%20/+/g
done <&0
