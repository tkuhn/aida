#!/bin/bash
#
# Usage:
# $ scripts/make-openaccess-table.sh
#

GENERAL=`\
  cat usecases/openaccess.md \
    | egrep '^- GENERAL. "' \
    | sed -r 's/^- GENERAL. "(.*)"$/\1/' \
  `

TEMPLATE=`\
  cat usecases/openaccess.md \
    | egrep '^- TEMPLATE. "' \
    | sed -r 's/^- TEMPLATE. "(.*)"$/\1/' \
  `

echo "SOURCE,RELATION,AIDA-SENTENCE" \
  > tables/openaccess.csv

cat usecases/openaccess.md \
  | egrep '^- [a-z]+\. [^ ]+( ".+")?$' \
  | sed -r "s/^- ([a-z]+)\. ([^ ]+)$/\2,\1,\"$GENERAL\"/" \
  | sed -r "s/^- ([a-z]+)\. ([^ ]+) \"(.+)\"$/\2,\1,\"$TEMPLATE\"@\3/" \
  | sed -r 's/QUALIFICATION(.*)@(.*)$/\2\1/' \
  >> tables/openaccess.csv
