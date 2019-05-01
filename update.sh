#!/bin/sh

DIR=~/test.mwatelescope.org/citations

# These lines create the citations.txt files (e.g. MWA_citations.txt)
# They contain bibcode of each paper in the library, publication date,
# and publication date of all citations (in mjd)
# e.g. 2012rsri.confE..36T [55927]: 57754,57296,56474
python ./ads_get_cites.py -o $DIR MWA
python ./ads_get_cites.py -o $DIR MWA-external
python ./ads_get_cites.py --user=55b946da9a -o $DIR pre-MWA

# Converts citations.txt files to json format
python ./cites2json.py -o $DIR -v MWA
python ./cites2json.py -o $DIR -v MWA-external
python ./cites2json.py -o $DIR -v pre-MWA

# Combine all papers and convert that to JSON too
cat $DIR/MWA_citations.txt $DIR/MWA-external_citations.txt $DIR/pre-MWA_citations.txt > $DIR/MWA-all_citations.txt
python ./cites2json.py -o $DIR -v MWA-all

# This plots three lines - MWA, MWA-external, pre-MWA
python ./combine_papers.py -o $DIR pre-MWA MWA MWA-external

# Replace the most cited bibcodes with human readable IDs
python replace_bibcodes.py $DIR/*.json
