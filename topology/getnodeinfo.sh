#!/bin/bash

routers=(1 248 2 252 3 4 5 6 7 10 11 13 14 15 17 19 20 21 22 27 29 30 32 33 35 36 37 38)

echo -n "Enter password: " 1>&2
read -s PASSWORD
echo 1>&2 

echo "site,adhoc0,adhoc1,adhoc0_txpwr,adhoc1_txpwr"

for router in "${routers[@]}"
  do
    echo -n "site$router ... " 1>&2
    read txpower0 txpower1 channel0 channel1 <<< \
    `sshpass -p $PASSWORD ssh -o ConnectTimeout=4 root@10.$router.1.1 "\
      /usr/sbin/iwlist adhoc0 txpower | grep -o '[0-9]* dBm' | grep -o '[0-9]*' || echo nil;\
      /usr/sbin/iwlist adhoc1 txpower | grep -o '[0-9]* dBm' | grep -o '[0-9]*' || echo nil;\
      /usr/sbin/iwlist adhoc0 channel | grep -o '(Channel [0-9]*)' | grep -o '[0-9]*' || echo nil;\
      /usr/sbin/iwlist adhoc1 channel | grep -o '(Channel [0-9]*)' | grep -o '[0-9]*' || echo nil"`
    if [ $? -eq 0 ]
      then
        [[ "$channel0" == "nil" ]] && channel0=''
        [[ "$channel1" == "nil" ]] && channel1=''
        [[ "$txpower0" == "nil" ]] && txpower0=''
        [[ "$txpower1" == "nil" ]] && txpower1=''
        echo $router,$channel0,$channel1,$txpower0,$txpower1
        echo "done." 1>&2
      else
        echo "unreachable." 1>&2
      fi
  done
