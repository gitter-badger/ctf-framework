
ROOT_UID=0
TIMEOUT=600
NC_PORT=88

password='####insert your password here####'

if [ "$UID" -ne "$ROOT_UID" ]
then 
    echo "The following script is using iptables."
    echo "Run it as a root"
    exit
fi

# The recall script.
# It will flush all your iptables rules
# if you will fukh up something.
# Do NOT remove this line until you are sure you have tested everything.
# screen -S flush-iptables -d -m bash -c "sleep $TIMEOUT && iptables -F" && echo "Timeout for --flush iptables has been set to $TIMEOUT seconds"

### INSERT YOUR IPTABLES CODE HERE

iptables -A INPUT -p tcp --dport 513:49152 -j DROP

for (( ;; )) { 
	netcat -l -p $NC_PORT | \
	\
	while read line 
	do
		count=$(echo "$line" | grep -c "$password")
		if [ "$count" -eq 1 ]; then
			iptables -A INPUT -m recent --name auth --set
		fi
	done
	time_start=$(date +%H)
	time_stop=$(date +$(echo "($time_start+2) % 24" | bc):%M)
	time_start=$(date +"$time_start":%M)
	iptables -I INPUT -p tcp --dport 513:49152 -m recent --rcheck --name auth --seconds 10  -j ACCEPT -m time --timestart $time_start --timestop $time_stop
	sleep 1
}

###


