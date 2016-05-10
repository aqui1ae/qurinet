#!/bin/ash

# Charlie Le
#
# README:
# Run this script with a log filename as a parameter. This script will append
# to that file when it parses the tx/rx information.
#
# This script will be best when paired with a timer function e.g. cron.
# It currently looks at adhoc0 and adhoc1, however this can easily be adjusted.

# http://stackoverflow.com/questions/17066250/create-timestamp-variable-in-bash-script
timestamp() {
  date +"%T"
}

parse_if() {

ifinfo=$(cat /proc/net/dev | egrep $1)

if=$(echo $ifinfo | awk '{print $1}')

if [ -z $if ] 
  then
# This means that the interface is down because it wasn't found.
rx="0"
tx="0"
ls="DOWN"
else
rx=$(echo $ifinfo | awk '{print $2}')
tx=$(echo $ifinfo | awk '{print $10}')
ls="UP"
fi

echo "$1 $rx $tx $(timestamp) $ls"
}

LOG_FILE=$1
if [ $# -ne 1 ]
  then
      echo "Invalid parameters"
      echo "Usage: $1 output_file"
      exit 1
fi

parse_if adhoc0 >> $LOG_FILE
parse_if adhoc1 >> $LOG_FILE
