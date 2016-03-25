import json
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

IPERF_DIRECTORY = SCRIPT_DIR + '/iperf'
OLSR_DIRECTORY = SCRIPT_DIR + '/olsr'

INDEX_FOR_LOCAL_NAME = 2
INDEX_FOR_REMOTE_NAME = 1

COLOR_GREEN = '#00FF00'
COLOR_GOLD = '#FFD700'
COLOR_RED_PURPLE = '#A10C68'
COLOR_BLACK = '#000000'

COLOR_MPR_LINK = COLOR_RED_PURPLE
COLOR_NONMPR_LINK = COLOR_BLACK
COLOR_MPR_NODE = COLOR_GOLD
COLOR_NONMPR_NODE = COLOR_GREEN

def linkColor(source, target, nodeList):
    for node in nodeList:
        MPRSelectors = node['MPRSelector'].split(',')
        if node['name'] == source and target in MPRSelectors \
        or node['name'] == target and source in MPRSelectors:
            return COLOR_MPR_LINK
    return COLOR_NONMPR_LINK

# Generate node JSON objects from the olsr JSON output
nodeList = []
for olsr_file in os.listdir(OLSR_DIRECTORY):
    # Each OLSR file is generated from a node, which is what will be focused on
    with open(OLSR_DIRECTORY + '/' + olsr_file) as olsrjsonfile:
        olsrjsonobj = json.loads(olsrjsonfile.read())

        # Get all of the site names that the node is an MPR for
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

# Generate connection JSON objects from the iperf JSON output
connections = []
for iperf_file in os.listdir(IPERF_DIRECTORY):
    with open(IPERF_DIRECTORY + '/' + iperf_file) as jsonfile:
        jsonobj = json.loads(jsonfile.read())

        connection = jsonobj['start']['connected'][0]
        source = connection['local_host'].split('.')[INDEX_FOR_LOCAL_NAME]
        target = connection['remote_host'].split('.')[INDEX_FOR_REMOTE_NAME]

        connections.append({
            'source': source,
            'target': target,
            'bandwidth': int(jsonobj['end']['sum_received']['bits_per_second']),
            'linkColor': linkColor(source, target, nodeList)
        })

print json.dumps({
    'nodes': nodeList,
    'connections': connections
})
