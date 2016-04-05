import json
import os
import sys
import subprocess

TCPDUMP_DIRECTORY = 'tcpdump/'
FILE_BASE_NAME = 'tcpdump_'

SOURCE_IP = 2
SIZE = 12
TIME = 1

TC = '202'
HELLO = '201'
MID = '3'
HNA = '4'

"""
Valid JSON (RFC 4627) 
Test on https://jsonformatter.curiousconcept.com/# after removing "//" comments.
[
  {
    "router": "site102",
    "fileinfo": 
    [
        { 
            "node": "10.0.102.2",
            "details": 
            [
                {
                    "time": 5.250670,
                    "size": 68,
                    "HNA": 1,
                    "TC": 2,
                    "HELLO": 3,
                    "MID": 4
                },
                {
                    "time": 296.396242,
                    "size": 88,
                    "HNA": 1,
                    "TC": 2,
                    "HELLO": 3,
                    "MID": 4
                }
            ]
        },
        
        { 
            "node": "10.0.101.2",
            "details": 
            [
                {
                    "time": 3.130450,
                    "size": 68,
                    "HNA": 1,
                    "TC": 2,
                    "HELLO": 3,
                    "MID": 4
                },
                {
                    "time": 296.396242,
                    "size": 88,
                    "HNA": 1,
                    "TC": 2,
                    "HELLO": 3,
                    "MID": 4
                }
            ]
        }
    ] //End "fileinfo" for router 102
  }[,] //End router "102", which is tcpdump_site102. Put comma for next file.
] 
"""

nodeList = []


for tcpdump_file in os.listdir(TCPDUMP_DIRECTORY):
    router = tcpdump_file.split('_')[1]
    output = subprocess.check_output("tshark -r " + (TCPDUMP_DIRECTORY + tcpdump_file) + " -R olsr -2", shell=True)
    summary = output.split('\n')
    
    output = subprocess.check_output("tshark -r " + (TCPDUMP_DIRECTORY + tcpdump_file) + " -R olsr -2 -T fields -e olsr.message_type", shell=True)
    numbers = output.split('\n')
    
    #auxiliary variables
    data = {}
    
    #JSON file variables
    fileinfo = []
    
    for entry in range(len(summary)):
        packet = summary[entry]
        message = numbers[entry]
        
        details = filter(None, packet.split(' '))
        types = message.split(',')
        
        if len(details) > 0:
            if data.has_key(details[SOURCE_IP]) == False:
	        data[details[SOURCE_IP]] = []

            data[details[SOURCE_IP]].append({
              'time':  float(details[TIME]),
              'size':  int(details[SIZE]),
              'HNA':   types.count(HNA),
              'TC':    types.count(TC),
              'HELLO': types.count(HELLO),
              'MID':   types.count(MID)
            })
            
    for key, val in data.items():
        fileinfo.append({
            'node': key,
            'details': val
        })
        
    nodeList.append({
        'router': router,
        'fileinfo':fileinfo
    })

print json.dumps(nodeList)
            
            
            
        
        
