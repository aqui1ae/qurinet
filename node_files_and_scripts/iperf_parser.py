import argparse
import csv
import json
import numpy

IPERF_SUMMARY_FILENAME = 'iperfsummary.csv'
DETAIL_FILENAME = 'detail.csv'

parser = argparse.ArgumentParser(description='Parse some IPERF JSON')
parser.add_argument('filename', help='The filename of the IPERF JSON to parse.')
args = parser.parse_args()

def write_iperfsummary(jsonobj):
    five_number_summary = ['min', 'firstQuartile', 'median', 'thirdQuartile', 'max']
    fieldnames = ['local_host', 'local_port', 'remote_host', 'remote_port', 'start', 'end', 'bytes', 'bits_per_second'] + five_number_summary
    start = jsonobj['start']
    end = jsonobj['end']
    bandwidths = []
    for interval in jsonobj['intervals']:
        bandwidths.append(interval['sum']['bits_per_second'])
    summary = {}

    for connection in start['connected']:
        for key in connection:
            summary[key] = connection[key]
        break # Only need one connection

    percentiles = range(0, 101, 25)
    for i in range(len(percentiles)):
        summary[five_number_summary[i]] =numpy.percentile(bandwidths, percentiles[i])

    sum_received = end['sum_received']
    for key in sum_received:
        summary[key] = sum_received[key]

    print summary
    with open(IPERF_SUMMARY_FILENAME, 'w') as csvfile:
        print "Opened {} for writing".format(IPERF_SUMMARY_FILENAME)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({fieldname:summary[fieldname] for fieldname in fieldnames})

def write_detail(jsonobj):
    fieldnames = ['local_host', 'local_port', 'remote_host', 'remote_port', 'start', 'end', 'bytes', 'bits_per_second']
    start = jsonobj['start']
    summary = {}
    for connection in start['connected']:
        for key in connection:
            summary[key] = connection[key]
        break # Only need one connection

    with open(DETAIL_FILENAME, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for interval in jsonobj['intervals']:
            for key in interval['sum']:
                summary[key] = interval['sum'][key]
            writer.writerow({fieldname:summary[fieldname] for fieldname in fieldnames})

with open(args.filename) as jsonfile:
    jsonobj = json.loads(jsonfile.read())
    write_iperfsummary(jsonobj)
    write_detail(jsonobj)
