#!/bin/sh
#
#  ccdsload.sh
###########################################################################
#
#  Purpose:
# 	This script creates CCDS assocload
#       input file and invokes assocload
#
  Usage=ccdsload.sh
#
#  Env Vars:
#
#      See the configuration file
#
#  Inputs:
#
#      - Common configuration file -
#               /usr/local/mgi/live/mgiconfig/master.config.sh
#      - CCDS load configuration file - ccdsload.config
#      - input file - see python script header
#
#  Outputs:
#
#      - An archive file
#      - Log files defined by the environment variables ${LOG_PROC},
#        ${LOG_DIAG}, ${LOG_CUR} and ${LOG_VAL}
#      - Input files for vocload and assocload
#      - see vocload and assocload outputs
#      - Records written to the database tables
#      - Exceptions written to standard error
#      - Configuration and initialization errors are written to a log file
#        for the shell script
#
#  Exit Codes:
#
#      0:  Successful completion
#      1:  Fatal error occurred
#      2:  Non-fatal error occurred
#
#  Assumes:  Nothing
#
# History:
#
# lec	01/06/2010 - created
#

cd `dirname $0`
LOG=`pwd`/ccdsload.log
rm -rf ${LOG}

CONFIG_LOAD=../ccdsload.config

#
# verify & source the configuration file
#

if [ ! -r ${CONFIG_LOAD} ]
then
    echo "Cannot read configuration file: ${CONFIG_LOAD}"
    exit 1
fi

. ${CONFIG_LOAD}

#
#  Source the DLA library functions.
#

if [ "${DLAJOBSTREAMFUNC}" != "" ]
then
    if [ -r ${DLAJOBSTREAMFUNC} ]
    then
        . ${DLAJOBSTREAMFUNC}
    else
        echo "Cannot source DLA functions script: ${DLAJOBSTREAMFUNC}" | tee -a ${LOG}
        exit 1
    fi
else
    echo "Environment variable DLAJOBSTREAMFUNC has not been defined." | tee -a ${LOG}
    exit 1
fi

#####################################
#
# Main
#
#####################################

#
# createArchive including OUTPUTDIR, startLog, getConfigEnv
# sets "JOBKEY"
preload ${OUTPUTDIR}

#
# create input files
#
echo 'Running createInputFiles.py' >> ${LOG_DIAG}
${CCDSLOAD}/bin/createInputFiles.py >> ${LOG_DIAG}
STAT=$?
checkStatus ${STAT} "${CCDSLOAD}/bin/createInputFiles.py"

#
# run association load
#

# set to full path for assocload
CONFIG_LOAD=${CCDSLOAD}/ccdsload.config

echo "Running CCDS association load" >> ${LOG_DIAG}
${ASSOCLOADER_SH} ${CONFIG_LOAD} ${JOBKEY}
STAT=$?
checkStatus ${STAT} "${ASSOCLOADER_SH}/bin/AssocLoad.sh ${CONFIG_LOAD}"

#
# run postload cleanup and email logs
#
shutDown
