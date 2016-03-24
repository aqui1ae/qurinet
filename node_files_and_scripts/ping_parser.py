import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def _get_match_groups(ping_output, regex):
    match = regex.search(ping_output)
    if not match:
        raise Exception('Invalid PING output:\n' + ping_output)
    return match.groups()

def parse(ping_output):
    """
    Parses the `ping_output` string into a dictionary containing the following
    fields:
        `host`: *string*; the target hostname that was pinged
        `sent`: *int*; the number of ping request packets sent
        `received`: *int*; the number of ping reply packets received
        `packet_loss`: *int*; the percentage of  packet loss
        `minping`: *float*; the minimum (fastest) round trip ping request/reply
                    time in milliseconds
        `avgping`: *float*; the average round trip ping time in milliseconds
        `maxping`: *float*; the maximum (slowest) round trip ping time in
                    milliseconds
        `jitter`: *float*; the standard deviation between round trip ping times
                    in milliseconds
    """
    matcher = re.compile(r'PING ([a-zA-Z0-9.\-]+) \(')
    host = _get_match_groups(ping_output, matcher)[0]

    matcher = re.compile(r'(\d+) packets transmitted, (\d+) packets received, (\d+\.\d+)% packet loss')
    sent, received, packet_loss = _get_match_groups(ping_output, matcher)

    times = [float(time) for time in re.findall(r'.?time=(\d+\.\d+).?', ping_output)]

    try:
        matcher = re.compile(r'(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)')
        minping, avgping, maxping, jitter = _get_match_groups(ping_output,
                                                              matcher)
    except:
        minping, avgping, maxping, jitter = ['NaN']*4

    return {'host': host, 'sent': sent, 'received': received, 'packet_loss': packet_loss,
            'minping': minping, 'avgping': avgping, 'maxping': maxping,
            'jitter': jitter, 'times': times}

PING_DIRECTORY = SCRIPT_DIR + '/ping'

columns = []
RTTsummary = []
packetLoss = []
for filename in os.listdir(PING_DIRECTORY):
    with open(PING_DIRECTORY + '/' + filename) as pingfile:
        ping = parse(ping_output=pingfile.read())
        name = '{} -> {}'.format(filename.split('.')[0], ping['host'])
        columns.append([name] + ping['times'])
        RTTsummary.append({
            'name': name,
            'rtt min': ping['minping'],
            'rtt avg': ping['avgping'],
            'rtt max': ping['maxping'],
            'rtt mdev': ping['jitter']
        })
        packetLoss.append([name] + [float(ping['packet_loss'])])
print json.dumps({
    'columns': columns,
    'RTTsummary': RTTsummary,
    'packetLoss': packetLoss
})
