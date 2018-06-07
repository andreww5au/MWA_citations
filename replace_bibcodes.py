#!/usr/bin/env python

import argparse


a = argparse.ArgumentParser()
a.add_argument('--verbose', '-v', dest='verbose', default=False,
               action='store_true',
               help='Increase verbosity of output')
a.add_argument('files', metavar='files', type=str, nargs='*', default=[],
               help='*.uv files for which to calculate ant_metrics.')
args = a.parse_args()

bibcodes = ['2017ApJ...848L..12A', '2013PASA...30....7T', '2016ApJ...826L..13A',
            '2016Natur.530..453K', '2017MNRAS.464.1146H', '2013PASA...30...31B',
            '2014MNRAS.444..606O', '2015PASA...32...25W', '2015RaSc...50...52S',
            '2016MNRAS.461.3135B', '2015ITAP...63.5433S', '2013ApJ...769....5J',
            '2017PASA...34....3L', '2016ApJ...818...86B', '2013ExA....36..679W',
            '2016MNRAS.462.3115D', '2017arXiv170703517D', '2018MNRAS.475.4263O',
            '2018MNRAS.474..779G', '2018ApJ...856...31T', '2018MNRAS.474.4056M',
            '2017arXiv170703517D', '2017MNRAS.471.3974J', '2009IEEEP..97.1497L',
            '2008ISTSP...2..707M', '2007AJ....133.1505B', '2010PASP..122.1353O',
            '2007ApJ...665..618B', '2009PASP..121..857W']
readable = ["Abbot et al. '17", "Tingay et al. '13", "Abbot et al. '16",
            "Keane et al. '16", "Hurley-Walker et al. '17", "Bowman et al. '13",
            "Offringa et al. '14", "Wayth et al. '15", "Sutinjo et al. '15",
            "Barry et al. '16", "Sutinjo et al. '15", "Jacobs et al. '13",
            "Line et al. '17", "Bhat et al. '16", "Wu et al. '13",
            "Dai et al. '16", "Duchesne et al. '17", "O'Sullivan et al. '18",
            "Galvin et al. '18", "Tingay et al. '18'", "McKinley et al. '18",
            "Duchesne et al. '17", "Jordan et al. '17", "Lonsdale et al. '09",
            "Mitchell et al. '08", "Bowman et al. '07", "Ord et al. '10",
            "Bhat et al. '07", "Wayth et al. '09"]

for f in args.files:
    if args.verbose:
        print('Replacing text in file' + f)

    # Read in the file
    with open(f, 'r') as file:
        filedata = file.read()

    # Replace bibcodes with readable strings
    for b, r in zip(bibcodes, readable):
        filedata = filedata.replace(b, r)

    # Write the file out again
    with open(f, 'w') as file:
        file.write(filedata)
