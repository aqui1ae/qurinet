#! /bin/bash

while :
do
  #python ./iperf_parser.py | python -mjson.tool > bandwidth.json
  #python ./ping_parser.py | python -mjson.tool > pingRow.json
  python ./olsrd_parser.py | python -mjson.tool > topology.json
  python ./dev_parser.py   | python -mjson.tool > dev.json
  #python tcpdump_parser.py  > tcpdump.json
  
  #mv ./bandwidth.json ./Information\ Interface
  #mv ./pingRow.json ./Information\ Interface
  mv ./topology.json ./Information\ Interface
  #mv ./tcpdump.json ./Information\ Interface
  mv ./dev.json ./Information\ Interface

  sleep 10
done
