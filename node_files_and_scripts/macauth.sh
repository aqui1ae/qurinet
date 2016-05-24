#! /bin/bash
# http://stackoverflow.com/a/245925

echo "Type the MAC Address for authentication, followed by ENTER:"

read MAC_ADDRESS

echo "$MAC_ADDRESS" | grep -q -o -E '^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$'

if [ $? -eq 0 ]
  then
    echo "Valid"
  else
    echo "Invalid"
fi
