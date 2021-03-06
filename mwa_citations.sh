#!/usr/bin/env bash

# These lines create the citations.txt files (e.g. MWA_citations.txt)
# They contain bibcode of each paper in the library, publication date,
# and publication date of all citations (in mjd)
# e.g. 2012rsri.confE..36T [55927]: 57754,57296,56474
python ./ads_get_cites.py -o ./ MWA
python ./ads_get_cites.py -o ./ MWA-external
python ./ads_get_cites.py -o ./ pre-MWA

# Converts citations.txt files to json format
python ./cites2json.py -v MWA
python ./cites2json.py -v MWA-external
python ./cites2json.py -v pre-MWA

# Combine all papers
cat MWA_citations.txt MWA-external_citations.txt pre-MWA_citations.txt > MWA-all_citations.txt
python ./cites2json.py -v MWA-all

# This plots three lines - MWA, MWA-external, pre-MWA
python ./combine_papers.py pre-MWA MWA MWA-external

# Replace the most cited bibcodes with human readable IDs
python replace_bibcodes.py *.json
