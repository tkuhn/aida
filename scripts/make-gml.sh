#!/bin/bash
#
# Usage:
# $ scripts/make-gml.sh
#

echo "graph [ directed 0" \
  > exported/data.gml

cat tables/all-extended.csv \
  | egrep -v '^SOURCE,' \
  | sed -r 's_^([^,]*),([^,]*),\"(.*)\",([^,]*),([^,]*),([^,]*)$_edge [\n  source "\1"\n  target "\6>"\n]_' \
  >> exported/data.gml

echo "]" \
  >> exported/data.gml

