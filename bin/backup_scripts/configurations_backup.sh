#!/bin/bash
#this script will backup the configuration files listed below
#
$DAYS_TO_KEEP=60
BACKUP_DIR=/home/zibawabackup/config

FINAL_BACKUP_DIR=$BACKUP_DIR"`date +\%Y-\%m-\%d`-daily/"
 
        echo "Making backup directory in $FINAL_BACKUP_DIR"
 
        if ! mkdir -p $FINAL_BACKUP_DIR; then
                echo "Cannot create backup directory in $FINAL_BACKUP_DIR. Go and fix it!" 1>&2
                exit 1;
        fi;
 
cp /etc/nginx/conf.d/zibawa.conf ${FINAL_BACKUP_DIR}/nginx/zibawa.conf
cp /etc/rabbit/rabbitmq.config ${FINAL_BACKUP_DIR}/rabbitmq.config
cp /etc/grafana/grafana.ini ${FINAL_BACKUP_DIR}/grafana.ini
cp /etc/grafana/ldap.toml ${FINAL_BACKUP_DIR}/ldap.toml
cp /home/zibawa/zibawa/zibawa/settings.py ${FINAL_BACKUP_DIR}/settings.py




nice ${SLAPCAT} -n 0 > ${FINAL_BACKUP_DIR}/config.ldif
nice ${SLAPCAT} -n 1 > ${FINAL_BACKUP_DIR}/myserver.com.ldif

chmod 640 ${FINAL_BACKUP_DIR}/*.ldif

echo "Back ups completed in $FINAL_BACKUP_DIR"

# DAILY BACKUPS
 
# Delete daily backups n days old or more
find $BACKUP_DIR -maxdepth 1 -mtime +$DAYS_TO_KEEP -name "*-daily" -exec rm -rf '{}' ';'
 
