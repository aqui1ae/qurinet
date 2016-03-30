import json
import os
import sys
import glob


COLOR_GREEN = '#00FF00'
COLOR_GOLD = '#FFD700'
COLOR_RED_PURPLE = '#A10C68'
COLOR_BLACK = '#000000'

COLOR_MPR_LINK = COLOR_RED_PURPLE
COLOR_NONMPR_LINK = COLOR_BLACK
COLOR_MPR_NODE = COLOR_GOLD
COLOR_NONMPR_NODE = COLOR_GREEN

DEFAULT_BANDWIDTH = 1
FILE_TYPE = '.json'
IPERF_DIRECTORY = 'iperf/'
OLSR_DIRECTORY = 'olsr/'

OLSRfilenames = glob.glob(OLSR_DIRECTORY + '*' + FILE_TYPE)
IPERFfilenames = glob.glob(IPERF_DIRECTORY + '*' + FILE_TYPE)

if len(OLSRfilenames) <= 0:
    sys.exit()
    
connections = []
nodeList = []

def linkColor(source, target, nodeList):
    for node in nodeList:
        MPRSelectors = node['MPRSelector'].split(',')
        if node['name'] == source and target in MPRSelectors \
        or node['name'] == target and source in MPRSelectors:
            return COLOR_MPR_LINK
    return COLOR_NONMPR_LINK

for olsr_file in os.listdir(OLSR_DIRECTORY):
    with open(OLSR_DIRECTORY + olsr_file) as olsrjsonfile:
        olsrjsonobj = json.loads(olsrjsonfile.read())
        
        sites = []
        for neighbor in olsrjsonobj['neighbors']:
            if neighbor['multiPointRelaySelector']:
                sites.append(neighbor['ipAddress'].split('.')[2])
        
        nodeList.append({
            'name': olsrjsonobj['interfaces'][0]['ipv4Address'].split('.')[2],
            'willingness': olsrjsonobj['config']['willingness'],
            'state': COLOR_MPR_NODE if len(sites) else COLOR_NONMPR_NODE,
            'MPRSelector': ','.join(sites)
        })
        
with open(OLSRfilenames[0]) as olsrjsonfile:
    olsrjsonobj = json.loads(olsrjsonfile.read())      
    links = olsrjsonobj['topology']
    for pair in links:
        sourcenode = pair['lastHopIP'].split('.')[2]
        destinationnode = pair['destinationIP'].split('.')[2]
        
        bandwidth = DEFAULT_BANDWIDTH
        
        if os.path.isfile(IPERF_DIRECTORY + '0' + sourcenode + destinationnode + FILE_TYPE):
            with open(IPERF_DIRECTORY + '0' + sourcenode + destinationnode + FILE_TYPE) as iperfjsonfile:
                iperfjsonobj = json.loads(iperfjsonfile.read())
                bandwidth = int(iperfjsonobj['end']['sum_received']['bits_per_second'])
        elif os.path.isfile(IPERF_DIRECTORY + '1' + sourcenode + destinationnode + FILE_TYPE):
            with open(IPERF_DIRECTORY + '1' + sourcenode + destinationnode + FILE_TYPE) as iperfjsonfile:
                iperfjsonobj = json.loads(iperfjsonfile.read())
                bandwidth = int(iperfjsonobj['end']['sum_received']['bits_per_second'])
                
        connections.append({
            'source': pair['lastHopIP'].split('.')[2],
            'target': pair['destinationIP'].split('.')[2],
            'etx': float(1) / (float(pair['linkQuality']) * float(pair['neighborLinkQuality'])),
            'bandwidth': bandwidth,
            'linkColor': linkColor(sourcenode, destinationnode, nodeList)
        })
                
print json.dumps({
    'nodes': nodeList,
    'connections': connections
})
