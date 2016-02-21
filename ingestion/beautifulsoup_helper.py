import urllib2
import re
import models
from bs4 import BeautifulSoup

def getAnchorCharacterListUrls(href):
    return href and re.compile('\/character_list\?\=*').search(href)

def getParserForUrl(url):
    print "Querying url: %s" % url
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html, 'html5lib')
    return soup

#VISIBLE FOR TESTING
def getParserContentsAsString(parser):
    return parser.encode('utf-8')
