#! /bin/bash

python ./iperf_parser.py | python -mjson.tool > bandwidth.json
python ./ping_parser.py | python -mjson.tool > pingRow.json
python ./olsrd_parser.py | python -mjson.tool > topology.json

mv ./bandwidth.json ./Information\ Interface
mv ./pingRow.json ./Information\ Interface
mv ./topology.json ./Information\ Interface
