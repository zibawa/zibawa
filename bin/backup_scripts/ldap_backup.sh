#!/bin/bash
#this script will backup the openLDAP config and data database for Zibawa
#make sure you carry out a test recovery to ensure it is compatible with
#your particular installation


DAYS_TO_KEEP=7
BACKUP_DIR=/home/zibawabackup/ldap/
SLAPCAT=/usr/sbin/slapcat

FINAL_BACKUP_DIR=$BACKUP_DIR"`date +\%Y-\%m-\%d`-daily/"
 
        echo "Making backup directory in $FINAL_BACKUP_DIR"
 
        if ! mkdir -p $FINAL_BACKUP_DIR; then
                echo "Cannot create backup directory in $FINAL_BACKUP_DIR. Go and fix it!" 1>&2
                exit 1;
        fi;
 

nice ${SLAPCAT} -n 0 > ${FINAL_BACKUP_DIR}config.ldif
nice ${SLAPCAT} -n 1 > ${FINAL_BACKUP_DIR}myserver.com.ldif

chmod 640 ${FINAL_BACKUP_DIR}*.ldif

echo "Back ups completed in $FINAL_BACKUP_DIR"

# DAILY BACKUPS
 
# Delete daily backups n days old or more
find $BACKUP_DIR -maxdepth 1 -mtime +$DAYS_TO_KEEP -name "*-daily" -exec rm -rf '{}' ';'
 

