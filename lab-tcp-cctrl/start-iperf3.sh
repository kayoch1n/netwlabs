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
docker-compose logs -t --no-log-prefix shioriko > output/ss-sender-raw.txt
docker-compose down
