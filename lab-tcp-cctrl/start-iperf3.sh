#!/bin/bash

if [[ `cat /proc/sys/net/ipv4/ip_forward` -ne 1 ]]; then
    echo "[host] ip forwarding is off"
    exit -1
fi

docker-compose up -d
ip=`docker exec setsuna dig setsuna +short`

echo "iperf using reno"
docker exec ayumu iperf3 -c $ip -C reno -t 10
sleep 5

echo "iperf using cubic"
docker exec ayumu iperf3 -c $ip -C cubic -t 10
sleep 1

echo "collect tcp statistics"
docker-compose logs -t --no-log-prefix shioriko > output/ss-sender.txt

function collapse_estab {
    sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "ESTAB"
}

# get timestamp
ts=$(cat output/ss-sender.txt | collapse_estab | grep "unacked" |  awk '{print $1}')
# get sender
send=$(cat output/ss-sender.txt | collapse_estab | grep "unacked" | awk '{print $6}')
# retransmissions - current, total
retr=$(cat output/ss-sender.txt | collapse_estab | grep -oP '\bunacked:.*\brcv_space'  | awk -F '[:/ ]' '{print $4","$5}' | tr -d ' ')
# get cwnd, ssthresh
cwnd=$(cat output/ss-sender.txt | collapse_estab |  grep "unacked" | grep -oP '\bcwnd:.*(\s|$)\bbytes_acked' | awk -F '[: ]' '{print $2","$4}')
# get smoothed RTT (in ms)
srtt=$(cat output/ss-sender.txt | collapse_estab |  grep "unacked" | grep -oP '\brtt:[0-9]+\.[0-9]+'  | awk -F '[: ]' '{print $2}')

echo "timestamp,sender,retr,cwnd,srtt" > output/ss-sender.csv
paste -d ',' <(printf %s "$ts") <(printf %s "$send") <(printf %s "$retr") <(printf %s "$cwnd") <(printf %s "$srtt") >> output/ss-sender.csv

docker-compose down


