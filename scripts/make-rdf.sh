#!/bin/bash
#
# Usage:
# $ scripts/make-rdf.sh
#

cat tables/all-extended.csv \
  | egrep -v '^SOURCE,' \
  | sed -r 's_^([^,]*),([^,]*),\"(.*)\",([^,]*),([^,]*),([^,]*)$_<\1> <http://purl.org/petapico/o/hycl#\2> <\6>_' \
  > exported/data.nt

