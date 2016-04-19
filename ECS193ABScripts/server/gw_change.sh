#! /bin/bash

while :; do

	curl http://localhost:9090/links | grep -v -E 'validityTime|systemTime|timeSinceStartup' > links.json
	sleep 5

	curl http://localhost:9090/links | grep -v -E 'validityTime|systemTime|timeSinceStartup' > links_temporary.json

	changes=$(diff links.json links_temporary.json)

	if [ "$changes" ] ; then


		>&2 echo "old:"
		>&2 echo 'localIP     remoteIP   linkCost'

		str=""
		while read line ; do
			if [[  $line == *"localIP"* ]] ; then
				str=$(echo "$line" | awk '{print $2}' | grep -o '".*"' | sed 's/"//g')
				>&2 echo -n "$str"
				>&2 echo -n '   '
				reading=true
			elif [[ $line == *"remoteIP"* ]] ; then
				str=$(echo "$line" | awk '{print $2}' | grep -o '".*"' | sed 's/"//g')
				>&2 echo -n "$str"
				>&2 echo -n '   '
			elif [[ $line == *"linkCost"* ]] ; then
				echo "$line" | awk '{print $2}' >&2
			fi
		done < links.json

		>&2 echo -e "\nnew:"
		>&2 echo 'localIP     remoteIP   linkCost'

		while read line ; do
			if [[  $line == *"localIP"* ]] ; then
				str=$(echo "$line" | awk '{print $2}' | grep -o '".*"' | sed 's/"//g')
				>&2 echo -n "$str"
				>&2 echo -n '   '
				reading=true
			elif [[ $line == *"remoteIP"* ]] ; then
				str=$(echo "$line" | awk '{print $2}' | grep -o '".*"' | sed 's/"//g')
				>&2 echo -n "$str"
				>&2 echo -n '   '
			elif [[ $line == *"linkCost"* ]] ; then
				echo "$line" | awk '{print $2}' >&2
			fi

		done < links_temporary.json
	fi

	sleep 3

done