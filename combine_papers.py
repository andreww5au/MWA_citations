#!/usr/bin/env python

from collections import OrderedDict
import operator,os,sys
import json
import numpy
from optparse import OptionParser,OptionGroup
import datetime

def cal_mjd(yr,mn,dy):
    """ convert calendar date to MJD
    year,month,day (may be decimal) are normal parts of date (Julian)"""
    
    m=mn
    if (yr<0):
        y=yr+1
    else:
        y=yr
    if (m<3):
        m+=12
        y-=1
    if (yr<1582 or (yr==1582 and (mn<10 or (mn==10 and dy<15)))):
        b=0
    else:
        a=int(y/100)
        b=int(2-a+a/4)
    
    jd=int(365.25*(y+4716))+int(30.6001*(m+1))+dy+b-1524.5
    mjd=jd-2400000.5

    return (mjd)
def mjd_cal(mjd):
    """convert MJD to calendar date (yr,mn,dy)
    """
    
    JD=mjd+2400000.5

    JD+=.5
    Z=int(JD)
    F=JD-Z
    if (Z<2299161):
        A=Z
    else:
        alpha=int((Z-1867216.25)/36524.25)
        A=Z+1+alpha-int(alpha/4)
    B=A+1524
    C=int((B-122.1)/365.25)
    D=int(365.25*C)
    E=int((B-D)/30.6001)
    day=B-D-int(30.6001*E)+F
    if (E<14):
        month=E-1
    else:
        month=E-13
    if (month<=2):
        year=C-4715
    else:
        year=C-4716

    return (year,month,day)
def mjd_datetime(mjd):
    year,month,day=mjd_cal(mjd)
    return datetime.datetime(year, month, int(day))

def datetime_mjd(dt):
    return cal_mjd(dt.year, dt.month, dt.day)

parser=OptionParser(usage='Usage: %prog [options] <library>\n')
parser.add_option('--out','-o',dest='out',default='.',
                  type='str',
                  help='Output directory [default=current directory]')
parser.add_option('--verbose','-v',dest='verbose',default=False,
                  action='store_true',
                  help='Increase verbosity of output')
(options, args) = parser.parse_args()

if len(args)==0:
    print 'Must supply >=1 library names'

dates=[]
publication=OrderedDict()
bibcodes=[]
for library in args:
    filename=os.path.join(options.out,'%s_citations.txt' % library)
    if not os.path.exists(filename):
        print 'Citation file %s does not exist' % filename
        sys.exit(1)
    dateoffile=filename.split('_')[-1].split('.')[0]
    f=open(filename)
    lines=f.readlines()

    curyear=datetime.datetime.now().year+(datetime_mjd(datetime.datetime.now())-
                                          cal_mjd(datetime.datetime.now().year, 1, 1))/365.25
    
    publication[library]=OrderedDict()

    for line in lines:
        d=line.split(':')[0]
        bibcode=d.split()[0]
        mjd_pub=int(d.split()[1].replace('[','').replace(']',''))
        dates.append(mjd_pub)
        publication[library][bibcode]=mjd_pub
        bibcodes.append(bibcode)


# these are the unique sorted dates
dates=sorted(set(dates))

sumofpapers=OrderedDict()
for library in args:
    sumofpapers[library]=OrderedDict()
    for date in dates:    
        sumofpapers[library][date]=0
        for bibcode in publication[library].keys():
            if publication[library][bibcode]<=date:
                sumofpapers[library][date]+=1
        

pubdata={}
pubdata['cols']=[]
pubdata['cols'].append({"id":"0", "label":"Date", "type":"date"})
for i,library in zip(range(len(args)),args):
    pubdata['cols'].append({"id":"%d" % (i+1), "label":library, "type":"number"})
pubdata['rows']=[]
for date in dates:
    z=[]
    t=mjd_datetime(date)
    z.append({'v': 'Date(%s)' % t.strftime('%Y, %m, %d')})
    for i,library in zip(range(len(args)),args):
        z.append({'v': sumofpapers[library][date]})
        pubdata['rows'].append({'c': z})

outpapers=os.path.join(options.out,'MWA_all_papers.json')
f=open(outpapers,'w')
f.write(json.dumps(pubdata,sort_keys=True))
f.close()
        
