#!/bin/bash
#
# Usage:
# $ scripts/make-npbotstudy-table.sh
#

echo "SOURCE,RELATION,AIDA-SENTENCE,TAX,GENE" \
  > tables/npbotstudy.csv

cat raw/npbotstudy.txt \
  | egrep -v '^#' \
  | egrep -v '^TAX,' \
  | sed -r 's/^([^,]*,[^,]*,[^,]*),([^"].*)$/\1,"\2"/' \
  | sed -r 's/^([^,]*),([^,]*),([^,]*),(".*")$/\3,claims,\4,\1,\2/' \
  | awk '{ print "http://identifiers.org/pubmed/"$0 }' \
  >> tables/npbotstudy.csv

