import json
import os
import sys

IPERF_DIRECTORY = 'iperf/'
INDEX_FOR_LOCAL_NAME = 2
INDEX_FOR_REMOTE_NAME = 1

bandwidthDetails = []
# Generate connection JSON objects from the iperf JSON output
for iperf_file in os.listdir(IPERF_DIRECTORY):
    with open(IPERF_DIRECTORY + iperf_file) as iperfjsonfile:
        iperfjsonobj = json.loads(iperfjsonfile.read())
        connection = iperfjsonobj['start']['connected'][0]

        bandwidthDetail = {}
        bandwidthDetail['average'] = iperfjsonobj['end']['sum_sent']['bits_per_second']
        bandwidthDetail['date'] = iperfjsonobj['start']['timestamp']['time']
        bandwidthDetail['name'] = "{} -> {}".format(connection['local_host'], connection['remote_host'])
        bandwidthDetail['data'] = []

        for interval in iperfjsonobj['intervals']:
            summary = interval['sum']
            bandwidthDetail['data'].append({
                'bandwidth': float(summary['bits_per_second']),
                'interval': float(summary['end'])
            })

        bandwidthDetails.append(bandwidthDetail)


print json.dumps({
    'bandwidthDetail' : bandwidthDetails
})
