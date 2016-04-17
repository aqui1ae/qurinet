import json
import os
import sys
import csv

DEV_DIRECTORY = 'dev/'

entries = []
# Generate connection JSON objects from the iperf JSON output
for dev_file in os.listdir(DEV_DIRECTORY):
    f = open(DEV_DIRECTORY + dev_file, 'rb')
    reader = csv.DictReader(f)
    siteNumber = dev_file.split('.')[0]
    entry = { }
    entry[siteNumber] = []       
    for row in reader:
      entry[siteNumber].append({
          'interface'  : row['IP'],
          'rx'         : row['RX'],
          'rx_packets' : row['RX_PACKETS'],
          'tx'         : row['TX'],
          'tx_packets' : row['TX_PACKETS']
      })

    entries.append(entry)

        

print json.dumps(entries)
