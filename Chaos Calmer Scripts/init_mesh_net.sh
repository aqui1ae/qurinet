#!/bin/bash
########################################################################
#
# Description : custom network script
#
# Authors     :
#
# Version     : 00.04 2015/09/13
#
# Notes       :
#
########################################################################
#Set path, this is here as a work-around so non-interactive ssh calls work
PATH=/bin:/sbin:/usr/bin:/usr/sbin

#get SITENO
. /boot/variables.conf
#get config variables
. /etc/netd/netd.conf.site$SITENO

#legacy - change hostname, why?
uci set system.@system[0].hostname=site$SITENO
uci commit system
echo $(uci get system.@system[0].hostname) > /proc/sys/kernel/hostname

#get available frequency channels from iw to convert ch# to freq
function getfreq()
{
  CHAN=$1
  MODE=$2
  echo "Translating into freq channel $CHAN mode $MODE"
  if [ $MODE = "11g" ]; then
    freq=`iw phy phy2 info | grep MHz | grep "\[$CHAN\]" | awk -F' ' '{if($2 < 5000) print $2 }'`
  fi

  if [ $MODE = "11a" ]; then
    freq=`iw phy phy2 info | grep MHz | grep "\[${CHAN}\]" | awk -F' ' '{if($2 > 5000) print $2 }'`
  fi
  
  return $freq
}

function wifi_destroy()
{
  if [ $WIFI0 -eq 1 ]
   then
    if [ $AHDEMO0 -eq 1 ]
     then
      iw dev adhoc0 del
    fi
    if [ $AP0 -eq 1 ]
     then
      iw dev wifi0 del
    fi
  fi
  if [ $WIFI1 -eq 1 ]
   then
    if [ $AHDEMO1 -eq 1 ]
     then
      iw dev adhoc1 del
    fi
    if [ $AP1 -eq 1 ]
     then
      iw dev wifi1 del
    fi
  fi
}


function phy_config(){
  PHY=$1
  POWER=$2
  DISTANCE=$3
  RTS=$4
  FRAG=$5

  iw phy $PHY set txpower fixed 20dBm
  #delete iw phy $PHY set coverage 30
  #distance calculates coverage class
  #this determines some timings based on time-of-flight delays
  iw phy $PHY set distance $DISTANCE
  if [[ $RTS ]]
   then
    iw phy $PHY set rts $RTS
  fi
  if [[ $FRAG ]]
   then
    iw phy $PHY set frag $FRAG
  fi
}

function ahdemo_config()
{
  DEV=$1
  PHY=$2
  CHAN=$3
  
  echo "Creating an adhoc interface $PHY $DEV"

  iw phy $PHY interface add $DEV type adhoc
  iw phy $PHY set antenna 1 1
  ip link set ${DEV} down
  sleep 1s
  mod=`ifconfig ${DEV} | grep HWaddr | awk -F' ' '{print $5}' | awk -F':' '{ print "0A:"$2":"$3":"$4":"$5":"$6 }'`
  ip link set dev $DEV address $mod
  sleep 1s
}


function ap_config()
{
  DEV=$1
  PHY=$2
  MODE=$3
  CHAN=$4
  INF=$5

  echo "Creating an AP interface $PHY $DEV $MODE $CHAN"

  # Create a new device, station mode, hostapd does the remaining (ath5k and ath9k do not allow the use of ap anymore, hostapd is used instead)
  iw phy $PHY interface add $DEV type station
  # Change the mac address
  sleep 1s
  echo "Starting hostapd for $DEV"
  # Hostapd, create the config file
  echo "interface=${DEV}" > /tmp/${DEV}.conf 
  if [ ${DEV} = "wifi0" ] ; then
    echo “ssid=qurinet0” >> /tmp/${DEV}.conf
  else
    echo “ssid=qurinet1” >> /tmp/${DEV}.conf
  fi

  echo "channel=$CHAN" >> /tmp/${DEV}.conf
  if [ $MODE = "11g" ]; then
    echo "hw_mode=g" >> /tmp/${DEV}.conf  
  fi
  if [ $MODE = "11a" ]; then                              
    echo "hw_mode=a" >> /tmp/${DEV}.conf            
  fi 
  # Mac address filtering, set to 0 to disable
  echo "macaddr_acl=0" >> /tmp/${DEV}.conf
  # echo "accept_mac_file=/etc/mac_whitelist" >> /tmp/${DEV}.conf

  # Start hostapd
  hostapd /tmp/${DEV}.conf -B
  sleep 1s
  # Start link
  ip link set $DEV up
}

function ahdemo_up()
{
  DEV=$1
  IP=$2
  MASK=$3
  MODE=$4
  CHAN=$5

  echo "UP an adhoc interface $DEV $IP $MASK $CHAN $MODE"

  ip addr add $IP/$MASK dev ${DEV} brd +
  ip link set ${DEV} up

  sleep 1s
  
  getfreq $CHAN $MODE
  echo "Operating on channel $CHAN"
  echo "Operating at freq $freq"
  iw dev $DEV ibss join "qurinet" $freq HT20 fixed-freq 22:22:22:22:22:22
  
}


function bridge_up()
{
  echo "UP bridge $IP_BR0 $MASK_BR0"
   # eth0
  ip link set eth0 up
      
  /usr/sbin/brctl addbr br0
  /usr/sbin/brctl addif br0 eth0

  if [ $WIFI0 -eq 1 -a $AP0 -eq 1 ]; then
    /usr/sbin/brctl addif br0 wifi0
  fi
  if [ $WIFI1 -eq 1 -a $AP1 -eq 1 ]; then
    /usr/sbin/brctl addif br0 wifi1
  fi
  sleep 1s
         
  ip addr add $IP_BR0/$MASK_BR0 dev br0 brd +
  ip link set br0 up

  if [ -n "${IP_BR0_1+x}" ]; then
    echo "Setting up BR0:1 $IP_BR0_1"
    ifconfig br0:1 $IP_BR0_1 netmask $MASK_BR0_1 broadcast ${BRD_BR0_1}
  fi
    
  sleep 1s
}

function bridge_down()
{
  ip link set br0 down
  if [ $WIFI0 -eq 1 -a $AP0 -eq 1 ]; then
    ip link set wifi0 down
  fi

  if [ $WIFI1 -eq 1 -a $AP1 -eq 1 ]; then
    ip link set wifi1 down
  fi
  ip link set eth0 down
  sleep 1s
}

function bridge_destroy()
{
  /usr/sbin/brctl delif br0 eth0
  
  if [ $WIFI0 -eq 1 -a $AP0 -eq 1 ]; then
    /usr/sbin/brctl delif br0 wifi0
  fi
  if [ $WIFI1 -eq 1 -a $AP1 -eq 1 ]; then
    /usr/sbin/brctl delif br0 wifi1
  fi
  
  /usr/sbin/brctl delbr br0
  sleep 1s
}


case "${1}" in
  start)
    echo "Starting custom network script"

    sleep 1s

    # wireless configuration
    if [ $WIFI0 -eq 1 ]; then
      PHY="phy2"
      phy_config $PHY $POWER0 $DIST0 $RTS0 $FRAG0
      if [ $AHDEMO0 -eq 1 ]; then
        ahdemo_config "adhoc0" $PHY $WIFI0_CHAN
        ahdemo_up "adhoc0" $IP_AHDEMO0 $MASK_AHDEMO0 $WIFI0_MODE $WIFI0_CHAN
        #legacy - seems excessive but will leave
        #sleep 20
      fi
      if [ $AP0 -eq 1 ]; then
        ap_config "wifi0" $PHY $WIFI0_MODE $WIFI0_CHAN "0"
      fi
    fi

    if [ $WIFI1 -eq 1 ]; then
      PHY="phy3"
      phy_config $PHY $POWER1 $DIST1 $RTS1 $FRAG1
      if [ $AHDEMO1 -eq 1 ]; then
        ahdemo_config "adhoc1" $PHY $WIFI1_CHAN
        ahdemo_up "adhoc1" $IP_AHDEMO1 $MASK_AHDEMO1 $WIFI1_MODE $WIFI1_CHAN
        #legacy - seems excessive so is skipped
        #sleep 20
      fi
      if [ $AP1 -eq 1 ]; then
        ap_config "wifi1" $PHY $WIFI1_MODE $WIFI1_CHAN "1"
      fi
    fi
    
    # bridge config, turns on eth0 and joins APs
    bridge_up

    # dhcp, uses new dnsmasq.conf.base 2015/03/19
    if [ $DHCPD -eq 1 ]; then
      killall dnsmasq
      cp /etc/dnsmasq.conf.base /etc/dnsmasq.conf
      touch /tmp/dnsmasq.leases
      echo "dhcp-range=$IP_PREFIX.$SITENO.100.100,$IP_PREFIX.$SITENO.100.199,12h" >> /etc/dnsmasq.conf
      dnsmasq
    fi

    if [ $OLSRD -eq 1 ]; then
      ${0} restart_olsr      
    else 
      echo "Setting static routes"
      
      #defined in netd.conf
      static_routes
      
    fi

    # iptables
    iptables -F INPUT
    iptables -F OUTPUT
    iptables -F FORWARD
    iptables -P INPUT ACCEPT
    iptables -P OUTPUT ACCEPT
    iptables -P FORWARD ACCEPT
    #default, allow everything
    #custom rules in netd.conf
    add_custom_rules
    
  ;;

  stop)
    echo "Stopping custom network script"

    if [ $WIFI0 -eq 1 -a $AHDEMO0 -eq 1 ]; then
      ip link set adhoc0 down
           fi
    
    if [ $WIFI1 -eq 1 -a $AHDEMO1 -eq 1 ]; then
      ip link set adhoc1 down
           fi

    # bridge
    bridge_down
    bridge_destroy

    killall hostapd

    wifi_destroy
    
    killall dnsmasq
    killall olsrd

    #remove routes
    ip route flush table main
    
    ;;

  restart|reload)
    ${0} stop
    sleep 1
    ${0} start
    ;;

  status)
    statusproc
    ;;

  restart_ap)
    #Stop all APs
    killall hostapd
    sleep 5 #wait for interfaces to die
    if [ $WIFI0 -eq 1 -a $AP0 -eq 1 ]
     then
      if [ -f /tmp/wifi0.conf ]
       then
        # Start hostapd
        echo "Starting hostapd on wifi0"
        hostapd /tmp/wifi0.conf -B
        sleep 1s
      else
        ap_config "wifi0" "phy2" $WIFI0_MODE $WIFI0_CHAN "0"
      fi
    fi
    if [ $WIFI1 -eq 1 -a $AP1 -eq 1 ]
     then
      if [ -f /tmp/wifi1.conf ]
       then
        # Start hostapd
        echo "Starting hostapd on wifi1"
        hostapd /tmp/wifi1.conf -B
        sleep 1s
      else
        ap_config "wifi1" "phy3" $WIFI1_MODE $WIFI1_CHAN "0"
      fi
    fi
    ;;
  restart_olsr)
    killall olsrd
    cp /etc/olsrd.conf.base /etc/olsrd.conf
    echo "Hna4 {" >> /etc/olsrd.conf
    echo "$IP_PREFIX.$SITENO.0.0 255.255.0.0" >> /etc/olsrd.conf
    echo "}" >> /etc/olsrd.conf
    olsrd -f /etc/olsrd.conf -d 0
    
    ;;

  *)
    echo "Usage: ${0} {start|stop|reload|restart|status|restart_ap|restart_olsr}"
    exit 1
    ;;
  esac

# End $rc_base/init.d/
