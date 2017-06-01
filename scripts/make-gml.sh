#!/bin/bash
#
# Usage:
# $ scripts/make-gml.sh
#

# Network file 1

echo "graph [ directed 0" \
  > exported/network1.gml

cat tables/all-extended.csv \
  | egrep -v '^SOURCE,' \
  | sed -r 's_^([^,]*),([^,]*),\"(.*)\",([^,]*),([^,]*),([^,]*)$_edge [\n  source "\1"\n  target "\6"\n]_' \
  >> exported/network1.gml

cat tables/all-extended.csv \
  | egrep -v '^SOURCE,' \
  | egrep '^[^,]*,[^,]*,\".*\",[^,]+,[^,]*,[^,]*$' \
  | sed -r 's_^([^,]*),([^,]*),\"(.*)\",([^,]*),([^,]*),([^,]*)$_edge [\n  source "\4"\n  target "\6"\n]_' \
  >> exported/network1.gml

cp exported/network1.gml exported/network2.gml

echo "]" \
  >> exported/network1.gml

# Network file 2

cat tables/all-extended.csv \
  | egrep -v '^SOURCE,' \
  | egrep '^[^,]*,[^,]*,\".*\",[^,]*,[^, ]* [^, ]*,[^,]*$' \
  | sed -r 's_^([^,]*),([^,]*),\"(.*)\",([^,]*),([^, ]*) ([^, ]*),([^,]*)$_edge [\n  source "\7"\n  target "\5"\n]\nedge [\n  source "\7"\n  target "\6"\n]_' \
  >> exported/network2.gml

cp exported/network2.gml exported/network3.gml

echo "]" \
  >> exported/network2.gml

# Network file 3

cat tables/spotlight-annotations.csv \
  | egrep -v '^SOURCE,' \
  | sed -r 's_^([^,]*),([^,]*)$_edge [\n  source "\1"\n  target "\2"\n]_' \
  >> exported/network3.gml

echo "]" \
  >> exported/network3.gml

