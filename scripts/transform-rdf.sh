#!/bin/bash
#
# Usage:
# $ scripts/transform-rdf.sh
#

rapper -i ntriples -o turtle exported/data.nt > exported/data.ttl
rapper -i ntriples -o rdfxml exported/data.nt > exported/data.rdf
