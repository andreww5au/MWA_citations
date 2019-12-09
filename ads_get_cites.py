#!/usr/bin/env python

import urllib2
from urllib2 import HTTPError
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import datetime
import os
import sys
from optparse import OptionParser, OptionGroup
import requests
import ads
import json


def cal_mjd(yr, mn, dy):
    """ convert calendar date to MJD
    year,month,day (may be decimal) are normal parts of date (Julian)"""

    m = mn
    if (yr < 0):
        y = yr + 1
    else:
        y = yr
    if (m < 3):
        m += 12
        y -= 1
    if (yr < 1582 or (yr == 1582 and (mn < 10 or (mn == 10 and dy < 15)))):
        b = 0
    else:
        a = int(y / 100)
        b = int(2 - a + a / 4)

    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + dy + b - 1524.5
    mjd = jd - 2400000.5

    return (mjd)


parser = OptionParser(usage='Usage: %prog [options] <library>\n')
parser.add_option('--out', '-o', dest='out', default='.',
                  type='str',
                  help='Output directory [default=current directory]')
parser.add_option('--refereed', dest='refereed', default=False,
                  action='store_true',
                  help='Only record refereed citations?')
parser.add_option('--verbose', '-v', dest='verbose', default=False,
                  action='store_true',
                  help='Increase verbosity of output')
parser.add_option('--token', '-t', dest='token',
                  default='TokenTokenToken',
                  help='ADS API token [default=%default]')
(options, args) = parser.parse_args()
if len(args) == 0:
    print 'Must supply >=1 library names'

ntries = 5  # Number of times to try a web query before giving up
lib_ids = {'pre-MWA': 'JYhgdTCNTmKhVcwUq0902A', 'MWA': 'LLDgjqnpQdS1fLMFuZ9h1A',
           'MWA-external': 'lGK81ZiLRNuDhAgv-23eCw'}
ads.config.token = options.token

for library in args:
    lib_id = lib_ids[library]
    # first get the list of paper IDs
    # The ads python API does not yet have libraries implemented, so we use the raw API
    tries = 0
    while tries < ntries:
    d = requests.get('https://api.adsabs.harvard.edu/v1/biblib/libraries/'
                     + lib_id, headers={"Authorization": "Bearer " + options.token},
                     params={"rows": 500})
        if d.status_code == 200:
            break
        else:
            tries += 1
            if tries >= ntries:
                raise ValueError('could not get list of bibcodes')
    bibcodes = map(str, d.json()['documents'])
    outname = os.path.join(options.out,
                           '%s_citations.txt' % (library))
    if options.verbose:
        print 'Writing to %s...' % outname
    f = open(outname, 'w')

    citations = {}
    for bibcode in bibcodes:
        if len(bibcode.strip()) == 0:
            continue
        bibcode = bibcode.strip()

        # get publication date
        payload = {"bibcode": [bibcode], 'format': '%D'}
        tries = 0
        while tries < ntries:
            r = requests.post('https://api.adsabs.harvard.edu/v1/export/custom',
                              headers={"Authorization": "Bearer " + options.token,
                                       "Content-type": "application/json"},
                              data=json.dumps(payload))
            if r.status_code == 200:
                break
            else:
                tries += 1
                if tries >= ntries:
                    raise ValueError('could not retrieve bibcode ' + bibcode)
        date = r.json()['export']
        month, year = map(int, date.split('/'))
        if month > 0:
            mjd_pub = int(cal_mjd(year, month, 1))
        else:
            mjd_pub = int(cal_mjd(year, 1, 1))

        # Get citations
        fields = ['bibcode', 'pubdate']
        query = 'citations(bibcode:' + bibcode + ')'
        if options.refereed:
            query += ' AND property:refereed'
        cites = ads.SearchQuery(q=query, fl=fields, rows=2000)
        citelist = list(cites)
        for cite in citelist:
            year, month, day = map(int, cite.pubdate.split('-'))
            if month > 0:
                mjd = int(cal_mjd(year, month, 1))
            else:
                mjd = int(cal_mjd(year, 1, 1))
            if bibcode in citations.keys():
                citations[bibcode].append(mjd)
            else:
                citations[bibcode] = [mjd]

        if bibcode in citations.keys():
            if options.verbose:
                print '%d citations for %s' % (len(citations[bibcode]), bibcode)
            f.write('%s [%d]: %s\n' % (bibcode, mjd_pub,
                                       ','.join(map(str, citations[bibcode]))))
        else:
            citations[bibcode] = []
            if options.verbose:
                print 'no citations for %s' % bibcode
            f.write('%s [%d]:\n' % (bibcode, mjd_pub))

    f.close()
