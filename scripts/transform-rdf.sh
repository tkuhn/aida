#!/bin/bash
#
# Usage:
# $ scripts/transform-rdf.sh
#

rapper -i ntriples -o turtle rdf/data.nt > rdf/data.ttl
