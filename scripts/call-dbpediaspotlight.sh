#!/bin/bash
#
# Usage:
# $ scripts/call-dbpediaspotlight.sh This+is+an+AIDA+sentence.
#

curl -s -H "Accept: text/turtle" "http://model.dbpedia-spotlight.org/en/annotate?text=$1&confidence=0.5" \
  | grep "itsrdf:taIdentRef" \
  | sed -r "s_\s*itsrdf:taIdentRef\s*<(.*)>\$_http://purl.org/aida/$1,\1_"
