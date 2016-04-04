#! /bin/bash

# assumes script is in home directory
# run with crontab
# */5 * * * * /root/run_tcpdump.sh

username='lc93-1'
hostip='10.102.100.188'
remotepath="/home/lc93-1/Classes/ECS193A/qurinet/ECS193AB\ Scripts/client/tcpdump"

cd

tcpdump -G 300 -W 1 -w tcpdump_$HOSTNAME -i adhoc0
scp tcpdump_$HOSTNAME $username@$hostip:"${remotepath}"
