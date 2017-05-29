#!/bin/bash
#
# Usage:
# $ scripts/make-npuserstudy-table.sh
#

echo "SOURCE,RELATION,AIDA-SENTENCE" \
  > tables/npuserstudy.csv

cat raw/npuserstudy-task1.txt \
  | egrep -v '^#' \
  | sort -u \
  | awk '{ print "http://identifiers.org/pubmed/11218245,claims,\""$0"\"" }' \
  >> tables/npuserstudy.csv

cat raw/npuserstudy-task2.txt \
  | egrep -v '^#' \
  | sort -u \
  | awk '{ print "http://identifiers.org/pubmed/20803876,claims,\""$0"\"" }' \
  >> tables/npuserstudy.csv

cat raw/npuserstudy-task3.txt \
  | egrep -v '^#' \
  | sort -u \
  | awk '{ print "http://identifiers.org/pubmed/17667027,claims,\""$0"\"" }' \
  >> tables/npuserstudy.csv

cat raw/npuserstudy-task4.txt \
  | egrep -v '^#' \
  | sort -u \
  | awk '{ print "http://identifiers.org/pubmed/14571757,claims,\""$0"\"" }' \
  >> tables/npuserstudy.csv

cat raw/npuserstudy-task5.txt \
  | egrep -v '^#' \
  | sort -u \
  | awk '{ print "http://identifiers.org/pubmed/10700716,claims,\""$0"\"" }' \
  >> tables/npuserstudy.csv
