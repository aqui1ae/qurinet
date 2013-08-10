#!/bin/bash

routers=(1 248 2 252 3 4 5 6 7 10 11 13 14 15 17 19 20 21 22 27 29 30 32 33 35 36 37 38)

echo -n "Enter password: "
read -s PASSWORD
echo 

for router in "${routers[@]}"
  do
    echo -n "site$router ... "
    ping 10.$router.1.1 -w 5 &>/dev/null
    if [ $? -eq 0 ]
      then
        echo "$PASSWORD" | ./scan-site $router 0 
        echo "$PASSWORD" | ./scan-site $router 1 
        echo "done."
      else 
        echo "unreachable."
    fi
  done
