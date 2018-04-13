#!/bin/bash
#
# Usage:
# $ scripts/make-spotlight-eval-table.sh
#

cat tables/spotlight-annotations.csv \
  | sed '1d' \
  | sed -r 's_^http://purl.org/aida/(.*),([^,]*)$_\1,\2_' \
  | sed 's/\+/ /g' \
  | shuf \
  > tables/spotlight-eval.csv
