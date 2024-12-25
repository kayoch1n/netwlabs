FROM ubuntu:22.04

# docker build . -f Dockerfile -t ccr.ccs.tencentyun.com/nijigasaki/azuna:net  
RUN apt-get update && apt-get install iproute2 conntrack iptables net-tools python3 curl iputils-ping vim -y

WORKDIR /data/azuna
