#!/usr/local/bin/python

##########################################################################
#
# Purpose:
#       From CCDSO input file create assocload input file
#
# Usage: createInputFiles.py
# Env Vars:
#	 1. OUTFILE_NAME
#
# Inputs:
#	CCDS.current.txt
#
#	   field 3: gene
#	   field 4: gene id
#	   field 5: ccds id
#
# Outputs:
#	 A tab-delimited file in assocload format:
#
#	    line 1 header: "MGI" "CCDS"
#
# 	    field 1: MGI ID
#           field 2: CCDS ID
# 
# Exit Codes:
#
#      0:  Successful completion
#      1:  An exception occurred
#
#  Assumes:  Nothing
#
#  Notes:  None
#
###########################################################################

import sys
import os
import mgi_utils
import string
import db

db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

print '%s' % mgi_utils.date()

# paths to input and two output files
ldbname = os.environ['ASSOC_EXTERNAL_LDB']
inFilePath = os.environ['INFILE_NAME_CCDS']
assocFilePath= os.environ['INFILE_NAME']

# file descriptors

# input
inFile = ''
# output for assocload
assocFile = ''

TAB= '\t'
CRT = '\n'
SPACE = ' '

#
# Initialize
#

try:
    inFile = open(inFilePath, 'r')
except:
    exit('Could not open file for reading %s\n' % inFilePath)

try:
    assocFile = open(assocFilePath, 'w')
except:
    exit('Could not open file for writing %s\n' % assocFilePath)

#
# Get Primary Mouse Markers/EntrezGene IDs
#
results = db.sql('''
        select a.accID, a._Object_key, aa.accID as mgiID
        from ACC_Accession a, ACC_Accession aa, MRK_Marker m
        where a._MGIType_key = 2 
        and a._LogicalDB_key = 55 
        and a._Object_key = aa._Object_key
        and a.preferred = 1
        and aa._MGIType_key = 2 
        and aa._LogicalDB_key = 1
        and aa.preferred = 1
	and a._Object_key = m._Marker_key
	and m._Organism_key = 1
	and m._Marker_Status_key = 1
        ''', 'auto')
egID = {}
for r in results:
    key = r['accID']
    value = r['mgiID']
    egID[key] = value

#
# Process
#

# write out assocload header
assocFile.write('%s%s%s%s' % ('MGI', TAB, ldbname, CRT))

# throw away header line
header = inFile.readline()

for line in inFile.readlines():

    tokens = string.split(line, TAB)
    gene = tokens[2]
    geneID = tokens[3]
    ccdsID = tokens[4]

    if egID.has_key(geneID):
        assocFile.write('%s%s%s%s' % (egID[geneID], TAB, ccdsID, CRT))
    else:
	print 'Invalid EntrezGene ID:  %s, gene ID: %s, ccdsID: %s\n' % (gene, geneID, ccdsID)

#
# Post Process
#

inFile.close()
assocFile.close()

print '%s' % mgi_utils.date()
