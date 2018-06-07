import json,numpy
import datetime
from astropy.time import Time
import pylab

d=json.loads(open('./MWA_papers.json').read())
t=[]
papers=[]
for v in d['rows']:
    papers.append(v['c'][1]['v'])
    d=datetime.datetime.strptime(v['c'][0]['v'],'Date(%Y, %m, %d)')
    t.append(Time(d).mjd)

pylab.clf()

pylab.step(t, papers)
pylab.xlabel('MJD')
pylab.ylabel('Cumulative Number of Papers')
