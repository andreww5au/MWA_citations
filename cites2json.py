#!/usr/bin/env python

from collections import OrderedDict
import operator
import os
import sys
import json
import numpy
from optparse import OptionParser, OptionGroup
import datetime


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


def mjd_cal(mjd):
    """convert MJD to calendar date (yr,mn,dy)
    """

    JD = mjd + 2400000.5

    JD += .5
    Z = int(JD)
    F = JD - Z
    if (Z < 2299161):
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    day = B - D - int(30.6001 * E) + F
    if (E < 14):
        month = E - 1
    else:
        month = E - 13
    if (month <= 2):
        year = C - 4715
    else:
        year = C - 4716

    return (year, month, day)


def mjd_datetime(mjd):
    year, month, day = mjd_cal(mjd)
    return datetime.datetime(year, month, int(day))


def datetime_mjd(dt):
    return cal_mjd(dt.year, dt.month, dt.day)

parser = OptionParser(usage='Usage: %prog [options] <library>\n')
parser.add_option('--out', '-o', dest='out', default='.', type='str',
                  help='Output directory [default=current directory]')
parser.add_option('--mincites', dest='mincites', default=0.03, type=float,
                  help='Min cites fraction for a single entry [default=%default]')
parser.add_option('--mincitesperyear', dest='mincitesperyear', default=0.03, type=float,
                  help='Min cites per year fraction for a single entry [default=%default]')
parser.add_option('--verbose', '-v', dest='verbose', default=False,
                  action='store_true',
                  help='Increase verbosity of output')
(options, args) = parser.parse_args()

if len(args) == 0:
    print 'Must supply >=1 library names'

for library in args:
    filename = os.path.join(options.out, '%s_citations.txt' % library)
    if not os.path.exists(filename):
        print 'Citation file %s does not exist' % filename
        sys.exit(1)
    f = open(filename)
    lines = f.readlines()

    curyear = datetime.datetime.now().year + (datetime_mjd(datetime.datetime.now()) -
                                              cal_mjd(datetime.datetime.now().year, 1, 1)) / 365.25

    citations = OrderedDict()
    citation_totals = OrderedDict()
    publication = OrderedDict()
    dates = []
    for line in lines:
        d = line.split(':')[0]
        bibcode = d.split()[0]
        mjd_pub = int(d.split()[1].replace('[', '').replace(']', ''))
        publication[bibcode] = mjd_pub
        data = line.split(':')[1].strip()
        if len(data) > 0:
            mjds = map(int, data.split(','))
            dates += mjds
            citations[bibcode] = mjds
        else:
            citations[bibcode] = []
        citation_totals[bibcode] = len(citations[bibcode])

    citationsperyear_totals = OrderedDict()
    for bibcode in citations.keys():
        citationsperyear_totals[bibcode] = len(citations[bibcode]) / (curyear - int(bibcode[:4]))

    totalcites = numpy.array(citation_totals.values()).sum()
    # set a minimum threshold for the number of citations
    # otherwise there are too many things to print
    mincites = int(options.mincites * totalcites)

    totalcitesperyear = numpy.array(citationsperyear_totals.values()).sum()
    # set a minimum threshold for the number of citations
    # otherwise there are too many things to print
    mincitesperyear = int(options.mincitesperyear * totalcitesperyear)

    sorted_bibcodes = [x[0] for x in sorted(citation_totals.items(), key=operator.itemgetter(1))]

    sortedperyear_bibcodes = [x[0] for x in sorted(citationsperyear_totals.items(),
                                                   key=operator.itemgetter(1))]

    # these are the unique sorted dates
    dates = sorted(set(dates))

    sumofcites = OrderedDict()
    sumofcitesperyear = OrderedDict()
    sumofpapers = OrderedDict()
    for date in dates:

        sumofcites[date] = OrderedDict()
        sumofcitesperyear[date] = OrderedDict()
        restofcites = 0
        restofcitesperyear = 0
        sumofpapers[date] = 0
        for bibcode in sorted_bibcodes:
            if publication[bibcode] <= date:
                sumofpapers[date] += 1
            if citation_totals[bibcode] >= mincites:
                sumofcites[date][bibcode] = (numpy.array(citations[bibcode]) <= date).sum()
            else:
                # bin it with all of the others
                restofcites += (numpy.array(citations[bibcode]) <= date).sum()
        for bibcode in sortedperyear_bibcodes:
            if citationsperyear_totals[bibcode] >= mincitesperyear:
                sumofcitesperyear[date][bibcode] = ((numpy.array(citations[bibcode]) <= date).sum() /
                                                    (curyear - int(bibcode[:4])))
            else:
                # bin it with all of the others
                restofcitesperyear += ((numpy.array(citations[bibcode]) <= date).sum() /
                                       (curyear - int(bibcode[:4])))
        sumofcites[date]['All Others'] = restofcites
        sumofcitesperyear[date]['All Others'] = restofcitesperyear
        print date, sumofpapers[date]

    data = {}
    data['cols'] = []
    data['cols'].append({"id": "0", "label": "Date", "type": "date"})

    for bibcode in sorted_bibcodes:
        j = len(data['cols'])
        if citation_totals[bibcode] >= mincites:
            label = bibcode
            data['cols'].append({"id": "%d" % j,
                                 "label": "%s" % label,
                                 "type": "number"})
    j = len(data['cols'])
    data['cols'].append({"id": "%d" % j,
                         "label": "All Others",
                         "type": "number"})
    dataperyear = {}
    dataperyear['cols'] = []
    dataperyear['cols'].append({"id": "0", "label": "Date", "type": "date"})

    for bibcode in sortedperyear_bibcodes:
        j = len(dataperyear['cols'])
        if citationsperyear_totals[bibcode] >= mincitesperyear:
            label = bibcode
            dataperyear['cols'].append({"id": "%d" % j,
                                        "label": "%s" % label,
                                        "type": "number"})
    j = len(dataperyear['cols'])
    dataperyear['cols'].append({"id": "%d" % j,
                                "label": "All Others",
                                "type": "number"})

    data['rows'] = []
    for date in dates:
        z = []
        # t=Time(date,format='mjd',scale='utc').datetime
        t = mjd_datetime(date)
        z.append({'v': 'Date(%s)' % t.strftime('%Y, %m, %d')})
        for bibcode in sumofcites[date].keys():
            z.append({'v': sumofcites[date][bibcode]})
        data['rows'].append({'c': z})

    dataperyear['rows'] = []
    for date in dates:
        z = []
        # t=Time(date,format='mjd',scale='utc').datetime
        t = mjd_datetime(date)
        z.append({'v': 'Date(%s)' % t.strftime('%Y, %m, %d')})
        for bibcode in sumofcitesperyear[date].keys():
            z.append({'v': sumofcitesperyear[date][bibcode]})
        dataperyear['rows'].append({'c': z})

    pubdata = {}
    pubdata['cols'] = []
    pubdata['cols'].append({"id": "0", "label": "Date", "type": "date"})
    pubdata['cols'].append({"id": "1", "label": "Papers", "type": "number"})
    pubdata['rows'] = []
    for date in dates:
        z = []
        t = mjd_datetime(date)
        z.append({'v': 'Date(%s)' % t.strftime('%Y, %m, %d')})
        z.append({'v': sumofpapers[date]})
        pubdata['rows'].append({'c': z})

    outtotal = os.path.join(options.out, '%s.json' % library)
    outperyear = os.path.join(options.out, '%speryear.json' % library)
    outpapers = os.path.join(options.out, '%s_papers.json' % library)
    f = open(outtotal, 'w')
    f.write(json.dumps(data, sort_keys=True))
    f.close()
    f = open(outperyear, 'w')
    f.write(json.dumps(dataperyear, sort_keys=True))
    f.close()
    f = open(outpapers, 'w')
    f.write(json.dumps(pubdata, sort_keys=True))
    f.close()
    if options.verbose:
        print 'Wrote %s, %s, and %s' % (outtotal,
                                        outperyear,
                                        outpapers)
