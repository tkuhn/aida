#!/bin/bash
#
# Usage:
# $ scripts/make-big-table.sh
#

echo "SOURCE,RELATION,AIDA-SENTENCE,VIA,COMPONENTS" \
  > tables/all.csv

tail -n +2 tables/papers.csv \
  | awk '{ print $0"," }' \
  >> tables/all.csv

tail -n +2 tables/alzheimers.csv \
  | awk '{ print $0",," }' \
  >> tables/all.csv

tail -n +2 tables/openaccess.csv \
  | awk '{ print $0",," }' \
  >> tables/all.csv

tail -n +2 tables/npuserstudy.csv \
  | awk '{ print $0",," }' \
  >> tables/all.csv

tail -n +2 tables/npbotstudy.csv \
  | sed -r 's/^([^,]*,[^,]*,".*"),([^, ]* [^, ]*)$/\1,,\2/' \
  >> tables/all.csv
