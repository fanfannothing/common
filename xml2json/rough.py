#!/usr/bin/python
"""
Rough parser for bad XML into JSON.
We assume the outer container is OUTERLABEL and each inner document label is DOCLABEL
"""

OUTERLABEL = "newdataset"
DOCLABEL = "vw_incidentpipeline_report"

import sys
import re
opentag = re.compile("<([^\/>]*)>")
closetag = re.compile("<\/([^>]*)>")

from common.json import dump
from common.stats import stats
import string

docs = []
currentdoc = {}
curtag = ""
curval = ""

print "["
for l in sys.stdin:
    if opentag.search(l):
        m = opentag.search(l)
        tag = m.group(1)
        if tag == OUTERLABEL:
            pass
        elif tag == DOCLABEL:
            pass
        else:
            curtag = tag
    elif closetag.search(l):
        m = closetag.search(l)
        tag = m.group(1)
        if tag == OUTERLABEL:
            pass
        elif tag == DOCLABEL:
            if len(currentdoc) > 0:
                docs.append(currentdoc)
                dump(currentdoc, sys.stdout, indent=4)
                print ","
            currentdoc = {}
        else:
            currentdoc[curtag] = string.strip(curval)
            curtag = ""
            curval = ""
    else:
        curval += l
print "]"
print >> sys.stderr, stats()
#dump(docs, sys.stdout)
