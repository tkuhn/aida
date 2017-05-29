#!/bin/bash
#
# Usage:
# $ scripts/make-openaccess-table.sh
#

TEMPLATE=`\
  cat usecases/alzheimers.md \
    | egrep '^- TEMPLATE. "' \
    | sed -r 's/^- TEMPLATE. "(.*)"$/\1/' \
  `

echo "PUBLICATION,RELATION,AIDA-SENTENCE" \
  > tables/alzheimers.csv

cat usecases/alzheimers.md \
  | egrep '^- [a-z]+\. (.*: )?"[^"]+"$' \
  | sed -r 's/^- ([a-z]+)\. (.*: )?"([^"]+)"$/,\1,"\3"/' \
  | sed -r "s/\"\.\.\. adverse event of (.+) \.\.\.\"/\"$TEMPLATE\"@\1/" \
  | sed -r 's/ADVERSE-EVENT(.*)@(.*)$/\2\1/' \
  | awk '{ print "http://dx.doi.org/10.1002/14651858.CD005593"$0 }' \
  >> tables/alzheimers.csv
