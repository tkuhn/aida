#!/bin/bash
#
# Usage:
# $ scripts/apply-dbpediaspotlight.sh
#

echo "AIDA-URI,COMPONENT" \
  > tables/spotlight-annotations.csv

cat tables/all-extended.csv \
  | egrep -v '^SOURCE,' \
  | sed -r 's_^([^,]*),([^,]*),\"(.*)\",([^,]*),([^,]*),http://purl.org/aida/([^,]*)$_scripts/call-dbpediaspotlight.sh "\6"_' \
  | bash \
  >> tables/spotlight-annotations.csv

