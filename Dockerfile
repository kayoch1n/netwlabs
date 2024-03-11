FROM ubuntu:22.04

RUN apt-get update && apt-get install iproute2 conntrack iptables net-tools python3 curl iputils-ping vim -y

WORKDIR /data/azuna
