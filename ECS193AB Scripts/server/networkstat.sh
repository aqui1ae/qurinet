#!/bin/bash

. /boot/variables.conf

iperf3 -4 -s &

declare -a interface_information

USER='djayasan'
HOSTIP='10.102.100.115'
IPERF_DIRECTORY='/home/djayasan/ECS193B/iperf'
OLSR_DIRECTORY='/home/djayasan/ECS193B/olsr'
PING_DIRECTORY='/home/djayasan/ECS193B/ping'

transfer_file_to_junction()
{
  filename=$1
  remote_path=$2
  scp $filename $USER@$HOSTIP:$remote_path
}

get_ip_and_nodenumber () 
{
  interface=$1
  matching_interface_ipv4=$(ifconfig $interface | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[1-3]{1,3}' | head -n 1)
  node_number=${matching_interface_ipv4:5}
  node_number=${node_number/\.[2-3]/}
  interface_information[0]=$matching_interface_ipv4
  interface_information[1]=$node_number
}


interface_to_neighbors=($(ip route | grep -E '[0-9]{1,3}\.[0-9]{1,3}\.0\.0/16 via [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[1-3]{1,3}' | awk '{print $5}'))

neighbor_ips=($(ip route | grep -E '[0-9]{1,3}\.[0-9]{1,3}\.0\.0/16 via [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[1-3]{1,3}' | awk '{print $3}'))

for ((node=0; node<${#neighbor_ips[*]}; node++));
do
  get_ip_and_nodenumber ${interface_to_neighbors[node]}
  
  local_matching_interface_ipv4=${interface_information[0]}
  local_node_number=${interface_information[1]}

  echo $local_matching_interface_ipv4 to ${neighbor_ips[node]}

  neighbor_node_number=${neighbor_ips[node]:5}
  neighbor_node_number=${neighbor_node_number/\.[2-3]/}

  interface_designator=$(echo -n ${interface_to_neighbors[node]} | tail -c 1)

  while :; do
    iperf3 -4 -B $local_matching_interface_ipv4 -c ${neighbor_ips[node]} -J > "$interface_designator$local_node_number$neighbor_node_number.json"  
    isIperfBusy=$(grep -o 'error' $interface_designator$local_node_number$neighbor_node_number.json | uniq)
    [[ $isIperfBusy = 'error' ]] || break
  done

  transfer_file_to_junction $interface_designator$local_node_number$neighbor_node_number.json $IPERF_DIRECTORY
  
done

get_ip_and_nodenumber ${interface_to_neighbors[0]}

curl http://localhost:9090/all > "${interface_information[1]}.json"

echo -e '{' | cat - ${interface_information[1]}.json > temp && mv temp ${interface_information[1]}.json

transfer_file_to_junction ${interface_information[1]}.json $OLSR_DIRECTORY

for ((node=0; node<${#neighbor_ips[*]}; node++));
do
  ping ${neighbor_ips[node]} -c 10 > "${interface_information[1]}.txt"
  transfer_file_to_junction ${interface_information[1]}.txt $PING_DIRECTORY
done


