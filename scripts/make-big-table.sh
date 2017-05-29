#!/bin/bash
#
# Usage:
# $ scripts/make-big-table.sh
#

echo "SOURCE,RELATION,AIDA-SENTENCE,VIA" \
  > tables/all.csv

tail -n +2 tables/papers.csv \
  >> tables/all.csv

tail -n +2 tables/alzheimers.csv \
  | awk '{ print $0"," }' \
  >> tables/all.csv

tail -n +2 tables/openaccess.csv \
  | awk '{ print $0"," }' \
  >> tables/all.csv
