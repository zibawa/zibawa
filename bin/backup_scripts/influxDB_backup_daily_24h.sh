#!/bin/bash
#This script will back up a the last 24 hours data for a single named database to the specified backup directory 
#To restore all history, you will need to keep all the backups- do not delete/rotate old versions


DB_NAME=dab51
BACKUP_DIR=/home/zibawa/backups/influxDB
DATE_FROM=$(date --rfc-3339=seconds --date='yesterday'| sed 's/ /T/')


echo "Backing up since $DATE_FROM"
FINAL_BACKUP_DIR=$BACKUP_DIR"/`date +\%Y-\%m-\%d`-daily/"${DB_NAME}"/"
 
        echo "Making backup directory in $FINAL_BACKUP_DIR"
 
        if ! mkdir -p $FINAL_BACKUP_DIR; then
                echo "Cannot create backup directory in $FINAL_BACKUP_DIR. Go and fix it!" 1>&2
                exit 1;
        fi;
 



influxd backup -database ${DB_NAME} -since ${DATE_FROM} ${FINAL_BACKUP_DIR}


echo "Back ups completed for ${DB_NAME} in $FINAL_BACKUP_DIR"







