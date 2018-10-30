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
parser.add_option('--user', dest='user', default='5a621dc7f1',
                  help='ADS user library ID [default=%default]')
parser.add_option('--verbose', '-v', dest='verbose', default=False,
                  action='store_true',
                  help='Increase verbosity of output')
(options, args) = parser.parse_args()
if len(args) == 0:
    print 'Must supply >=1 library names'

for library in args:
    # first get the list of paper IDs
    bibcodes = []
    values = {'libname': library, 'libid': options.user}
    d = requests.get('http://adsabs.harvard.edu/cgi-bin/nph-abs_connect/?library',
                     params=values)
    lines = d.content.split('\n')
    # url = "http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?library&libname=%s&libid=%s" % (library,
    #                                                                                          options.user)
    # try:
    #     u = urllib2.urlopen(url)
    #     lines = u.readlines()

    # except urllib2.HTTPError as e:
    #     lines=e.readlines()
    # except:
    #     print 'Unable to get library info from %s' % url
    #     sys.exit(1)
    # lines=[]
    for line in lines:
        if line.startswith('<tr>') and 'bibcode' in line:
            data = line.split('<')
            bibcodes.append(data[5].split()[3].replace('value="', '').replace('">&nbsp;', ''))
            print bibcodes[-1]

    # bibcodes=open('bibcodes_MWA.txt').readlines()
    # bibcodes=open('bibcodes_MWA-external.txt').readlines()
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
        url = 'http://adsabs.harvard.edu/abs/%s' % bibcode
        u = urllib2.urlopen(url)
        lines = u.readlines()
        for line in lines:
            if line.startswith('<tr>') and 'Publication Date' in line:
                data = line.split('<')
                date = data[9].split('>')[1]
                month, year = map(int, date.split('/'))
                if month > 0:
                    mjd_pub = int(cal_mjd(year, month, 1))
                else:
                    mjd_pub = int(cal_mjd(year, 1, 1))

        if options.refereed:
            url = 'http://adsabs.harvard.edu/cgi-bin/nph-ref_query?bibcode=%s&amp;refs=REFCIT&amp;db_key=AST' % bibcode
        else:
            url = 'http://adsabs.harvard.edu/cgi-bin/nph-ref_query?bibcode=%s&amp;refs=CITATIONS&amp;db_key=AST' % bibcode
        try:
            u = urllib2.urlopen(url)
            lines = u.readlines()
            for line in lines:
                if line.startswith('<tr>') and 'bibcode' in line:
                    data = line.split('<')
                    date = data[14].split('>')[1]
                    month, year = map(int, date.split('/'))
                    if month > 0:
                        mjd = int(cal_mjd(year, month, 1))
                    else:
                        mjd = int(cal_mjd(year, 1, 1))
                    if bibcode in citations.keys():
                        citations[bibcode].append(mjd)
                    else:
                        citations[bibcode] = [mjd]
            if options.verbose:
                print '%d citations for %s' % (len(citations[bibcode]), bibcode)
            f.write('%s [%d]: %s\n' % (bibcode, mjd_pub,
                                       ','.join(map(str, citations[bibcode]))))
        except urllib2.HTTPError:
            citations[bibcode] = []
            if options.verbose:
                print 'no citations for %s' % bibcode
            f.write('%s [%d]:\n' % (bibcode, mjd_pub))

    f.close()
