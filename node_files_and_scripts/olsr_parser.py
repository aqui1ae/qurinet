import argparse
import csv
import json

LINK_SET_FILENAME = 'linkset.csv'
NEIGHBOR_SET_FILENAME = 'neighbor.csv'
LINKINFO_SET_FILENAME = 'linkinfo.csv'

parser = argparse.ArgumentParser(description='Parse some OLSR JSON')
parser.add_argument('filename', help='The filename of the OLSR JSON to parse.')
args = parser.parse_args()

def write_csv(csvfilename, fieldnames, jsonarr):
    with open(csvfilename, 'w') as csvfile:
            print "Opened {} for writing".format(csvfilename)
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for jsonobj in jsonarr:
                writer.writerow({fieldname:jsonobj[fieldname] for fieldname in fieldnames})

def write_links(jsonobj):
    fieldnames = ['localIP', 'remoteIP', 'validityTime', 'linkQuality', 'neighborLinkQuality', 'linkCost']
    write_csv(LINK_SET_FILENAME, fieldnames, jsonobj['links'])

def write_neighbors(jsonobj):
    fieldnames = ['ipAddress', 'symmetric', 'multiPointRelay', 'multiPointRelaySelector', 'willingness', 'twoHopNeighborCount']
    write_csv(NEIGHBOR_SET_FILENAME, fieldnames, jsonobj['neighbors'])

def write_interfaces(jsonobj):
    fieldnames = ['ipv4Address', 'state', 'nameFromKernel', 'rxCompressed','rxCrcErrors','rxDropped','rxErrors','rxFifoErrors','rxFrameErrors','rxLengthErrors','rxMissedErrors','rxOverErrors','rxPackets','txAbortedErrors','txBytes','txCarrierErrors','txCompressed','txDropped','txErrors','txFifoErrors','txHeartbeatErrors','txPackets','txWindowErrors', 'wireless', 'olsrMTU']
    write_csv(LINKINFO_SET_FILENAME, fieldnames, jsonobj['interfaces'])

with open(args.filename) as jsonfile:
    jsonobj = json.loads(jsonfile.read())
    write_links(jsonobj)
    write_neighbors(jsonobj)
    write_interfaces(jsonobj)
