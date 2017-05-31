#!/bin/bash
#
# Usage:
# $ scripts/make-npbotstudy-table.sh
#

echo "SOURCE,RELATION,AIDA-SENTENCE,COMPONENTS" \
  > tables/npbotstudy.csv

cat raw/npbotstudy.txt \
  | egrep -v '^#' \
  | egrep -v '^TAX,' \
  | sed -r 's/^([^,]*,[^,]*,[^,]*),([^"].*)$/\1,"\2"/' \
  | sed -r 's_^([^,]*),([^,]*),([^,]*),(".*")$_\3,claims,\4,http://purl.uniprot.org/taxonomy/\1 http://www.ncbi.nlm.nih.gov/gene/\2_' \
  | awk '{ print "http://identifiers.org/pubmed/"$0 }' \
  >> tables/npbotstudy.csv

