import json
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

IPERF_DIRECTORY = SCRIPT_DIR + '/iperf'
bandwidthDetail = []
INDEX_FOR_LOCAL_NAME = 2
INDEX_FOR_REMOTE_NAME = 1

details = []
# Generate connection JSON objects from the iperf JSON output
for iperf_file in os.listdir(IPERF_DIRECTORY):
    with open(IPERF_DIRECTORY + '/' + iperf_file) as jsonfile:
        jsonobj = json.loads(jsonfile.read())
        connection = jsonobj['start']['connected'][0]
        for interval in jsonobj['intervals']:
            summary = interval['sum']
            details.append({
                'site': int(connection['local_host'].split('.')[INDEX_FOR_LOCAL_NAME]),
                'to': int(connection['remote_host'].split('.')[INDEX_FOR_REMOTE_NAME]),
                'bandwidth': float(summary['bits_per_second']),
                'interval': '{}-{}'.format(summary['start'], summary['end'])
            })
print json.dumps({
    'bandwidthDetail' : details
})
