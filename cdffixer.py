#!/usr/bin/env python

import sys
import response

if len(sys.argv) != 3:
    print 'Usage: cdffixer.py infile outfile'

infile_name = sys.argv[1]
outfile_name = sys.argv[2]

print 'Reading RMF ...'
rm = response.RedistributionMatrix(infile_name, fix_cdfs=True, scale_cdfs=False)

print 'Storing ...'
rm.store(outfile_name)
