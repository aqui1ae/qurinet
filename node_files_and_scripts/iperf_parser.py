import json
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

IPERF_DIRECTORY = SCRIPT_DIR + '/iperf'
INDEX_FOR_LOCAL_NAME = 2
INDEX_FOR_REMOTE_NAME = 1

bandwidthDetails = []
data = []
# Generate connection JSON objects from the iperf JSON output
for iperf_file in os.listdir(IPERF_DIRECTORY):
    with open(IPERF_DIRECTORY + '/' + iperf_file) as jsonfile:
        jsonobj = json.loads(jsonfile.read())
        connection = jsonobj['start']['connected'][0]

        bandwidthDetail = {}
        bandwidthDetail['name'] = "{} -> {}".format(connection['local_host'], connection['remote_host'])
        bandwidthDetail['data'] = data

        for interval in jsonobj['intervals']:
            summary = interval['sum']
            data.append({
                'bandwidth': float(summary['bits_per_second']),
                'interval': '{}'.format(summary['end'])
            })

        bandwidthDetails.append(bandwidthDetail)

print json.dumps({
    'bandwidthDetail' : bandwidthDetails
})
