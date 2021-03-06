#!/usr/bin/env python
"""
Method to convert html2text.

It uses the same procedure discussed in:
    http://github.com/turian/common-scripts/blob/master/html2text/README.txt
See that file, to understand the requirements.
Essentially, we pass the HTML through tidy then Bayer's html2text utility
(not aaronsw's html2text.py, mind you).

We can also use NCleaner = http://webascorpus.sourceforge.net/, converts
HTML to text and removes boilerplate. This cleans a lot more than html2text,
and is perhaps more suitable for text mining.

ISSUES: I may have the character encodings wrong :(
See http://github.com/turian/common-scripts/blob/master/html2text/README.txt
for more information.

TODO: Trap stderr output.
"""

from common.misc import runcmd
from common.tidy import tidy
import os.path

import sys
import tempfile, shutil, os
from common.stats import stats
import common.json
import re
import urllib,urllib2

def html2text(html, html2textrc=os.path.expanduser("~/dev/common-scripts/html2text/html2textrc"), forceoutput=True, veryquiet=True):
    """
    If veryquiet, all errors and warnings from tidy are written to /dev/null.
    """
    assert os.path.exists(html2textrc)
    tidyhtml = tidy(html, xml=False, forceoutput=forceoutput, veryquiet=veryquiet)
    text = runcmd("html2text -nobs -style pretty  -rcfile %s" % html2textrc, input=tidyhtml)
    return text

def batch_nclean(htmls, strip_html_output=True, ncleaner=os.path.join(os.environ["UTILS"], "bin/ncleaner")):
    """
    For a list of HTML byte strings, run ncleaner and return a list.
        NCleaner = http://webascorpus.sourceforge.net/, converts HTML to text and removes boilerplate.
    Return None if there was some error.
    strip_html_output=True means remove "<p>" or "<l>" which is inserted at the beginning of each segmented line.
    """
    indir = tempfile.mkdtemp()
    outdir = tempfile.mkdtemp()
    txts = None

    assert os.path.exists(ncleaner)

    htmlre = re.compile("^\s*<[^<>]*>\s*", re.MULTILINE)
    try:
        htmlfiles = ["%d.html" % i for i in range(len(htmls))]
        txtfiles = ["%d.txt" % i for i in range(len(htmls))]
        for f, html in zip(htmlfiles, htmls):
#            print os.path.join(indir, f)
            open(os.path.join(indir, f), "wb").write(html)
        cmd = "%s %s %s" % (ncleaner, indir, outdir)        
        print >> sys.stderr, "About to run NCleaner on %d files: %s..." % (len(htmlfiles), cmd)
        print >> sys.stderr, stats()
        os.system("%s %s %s" % (ncleaner, indir, outdir))
        print >> sys.stderr, "...done running NCleaner on %d files" % (len(htmlfiles))
        print >> sys.stderr, stats()
        txts = [open(os.path.join(outdir, txtfil)).read() for txtfil in txtfiles]
        if strip_html_output:
            txts = [htmlre.sub("\n", txt) for txt in txts]
        assert len(txts) == len(htmls)
    except:
        print >> sys.stderr, "Problem in batch_nclean: %s" % sys.exc_info()[0]
    shutil.rmtree(indir, ignore_errors=False, onerror=lambda function, path, excinfo: sys.stderr.write("Could not shutil.rmtree, function=%s, path=%s, excinfo=%s\n" % function, path, excinfo))
    shutil.rmtree(outdir, ignore_errors=False, onerror=lambda function, path, excinfo: sys.stderr.write("Could not shutil.rmtree, function=%s, path=%s, excinfo=%s\n" % function, path, excinfo))
    return txts

def boilerpipe_html2text(html):
    values = {"text": html.encode("utf-8"), "extractor": "DefaultExtractor", "output": "text"}
    data = urllib.urlencode(values)
    boilerpipe_response = urllib2.urlopen("http://localhost:8080/boilerpipe-api/extract", data)
    return boilerpipe_response.read().decode("utf-8")

def boilerpipe_url2text(url):
    """
    Use Kohlschuetter Search Intelligence's boilerpipe boilerplate stripper.
    """
    newurl = "http://boilerpipe-web.appspot.com/extract?url=%s+&extractor=ArticleExtractor&output=text" % urllib.quote_plus(url)
#    print newurl
    f = urllib2.urlopen(newurl)
    data = f.read()
    f.close()
    return data

#http://boilerpipe-web.appspot.com/extract?url=http%3A%2F%2Fnarrativebranding.wordpress.com%2F2010%2F08%2F18%2Fgone-fishin%2F+&extractor=ArticleExtractor&output=text

def diffbot_url2text(url, token):
    """
    Use diffbot article API: http://www.diffbot.com/docs/api/article
    """
    import urllib,urllib2
    newurl = "http://www.diffbot.com/api/article?token=%s&url=%s" % (token, urllib.quote_plus(url))
#    print newurl
    f = urllib2.urlopen(newurl)
    data = f.read()
    f.close()
    return common.json.loads(data)

    

if __name__ == "__main__":
#    import sys
#    print html2text(sys.stdin.read())
#    print boilerpipe_url2text("http://www.bianet.org/english/freedom-of-expression/122506-dairy-company-yorsan-advocates-for-internet-censorship")
    print common.json.dumps(diffbot_url2text("http://www.bianet.org/english/freedom-of-expression/122506-dairy-company-yorsan-advocates-for-internet-censorship", "XXXXX"), indent=4)
