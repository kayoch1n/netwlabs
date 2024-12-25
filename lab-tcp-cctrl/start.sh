#!/bin/bash
set -e

if [[ `cat /proc/sys/net/ipv4/ip_forward` -ne 1 ]]; then
    echo "[host] ip forwarding is off"
    exit -1
fi

docker-compose up -d
echo "[container] started"

function cont_run() {
    docker exec $1 bash -c "$2" 
}

# 在两个容器上分别获取router的IP地址
router_ayumu=`cont_run ayumu "dig router +short"`
router_setsuna=`cont_run setsuna "dig router +short"`

echo "[container:ayumu] add default route via ${router_ayumu}"
cont_run ayumu "ip route del default ; ip route add default via ${router_ayumu}"

echo "[container:setsuna] add default route via ${router_setsuna}"
cont_run setsuna "ip route del default ; ip route add default via ${router_setsuna}"

echo "[container:router] add traffic control"
cont_run router "tc qdisc add dev eth0 root handle 1: htb default 114"
cont_run router "tc class add dev eth0 parent 1: classid 1:114 htb rate 1Mbit"
cont_run router "tc qdisc add dev eth0 parent 1:114 handle 514: bfifo limit 0.1MB"
cont_run router "tc qdisc add dev eth1 root handle 1: htb default 114"
cont_run router "tc class add dev eth1 parent 1: classid 1:114 htb rate 1Mbit"
cont_run router "tc qdisc add dev eth1 parent 1:114 handle 514: bfifo limit 0.1MB"

echo "[container] setup done"
