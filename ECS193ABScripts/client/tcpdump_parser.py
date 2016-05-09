import json
import os
import sys
import subprocess

TCPDUMP_DIRECTORY = 'tcpdump/'
FILE_BASE_NAME = 'tcpdump_'

MAX_TIME = 60
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
    routerSummary = []
    summaryData = { }

    for entry in range(len(summary)):
        packet = summary[entry]
        message = numbers[entry]
        
        details = filter(None, packet.split(' '))
        types = message.split(',')
                 

        if len(details) > 0:
            if data.has_key(details[SOURCE_IP]) == False:
	        data[details[SOURCE_IP]] = []
                summaryData[details[SOURCE_IP]] = { }
                summaryData[details[SOURCE_IP]] = {
                   'size'  : 0,
                   'HNA'   : 0,
                   'TC'    : 0,
                   'HELLO' : 0,
                   'MID'   : 0,
                   'COUNT' : 0
                }
             
            summaryData[details[SOURCE_IP]]['size']  = summaryData[details[SOURCE_IP]]['size']  + int(details[SIZE])
            summaryData[details[SOURCE_IP]]['HNA']  = summaryData[details[SOURCE_IP]]['HNA']  + types.count(HNA)
            summaryData[details[SOURCE_IP]]['TC']  = summaryData[details[SOURCE_IP]]['TC']  + types.count(TC)
            summaryData[details[SOURCE_IP]]['HELLO']  = summaryData[details[SOURCE_IP]]['HELLO']  + types.count(HELLO)
            summaryData[details[SOURCE_IP]]['MID']  = summaryData[details[SOURCE_IP]]['MID']  + types.count(MID)
            summaryData[details[SOURCE_IP]]['COUNT']  = summaryData[details[SOURCE_IP]]['COUNT']  + 1
       
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

    for key, val in summaryData.items():
        val['size'] = (float(val['size']) / val['COUNT'])
        val['HNA'] = float(val['HNA'])
        val['TC'] = float(val['TC'])
        val['HELLO'] = float(val['HELLO'])
        val['MID'] = float(val['MID'])  
        routerSummary.append({
            'node': key,
            'Size per Minute': val['size'],
            'HNA per Minute': val['HNA'],
            'TC per Minute': val['TC'],
            'HELLO per Minute': val['HELLO'],
            'MID per Minute': val['MID']
        })
 
    nodeList.append({
        'router': router,
        'fileinfo':fileinfo,
        'summary': routerSummary
    })

print json.dumps(nodeList)
            
            
            
        
        
