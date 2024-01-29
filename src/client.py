import azuna
logger = azuna.get_logger(__file__)

def main():
    import socket
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', required=True)
    parser.add_argument('-p', '--port', required=True, type=int)
    parser.add_argument('--dev_name', default='yu0')

    args = parser.parse_args()
    
    address = socket.getaddrinfo(args.server, args.port)[0][-1]
    server_ip, _ = address

    dev_name = args.dev_name
    logger.info("create device %s", dev_name)
    t, mtu = azuna.create_tun(dev_name=dev_name, if_addr='10.8.0.2/16')
    
    logger.info("setup routing")
    default_gw = azuna.run("ip route show 0/0 | sed -e 's/.* via \([^ ]*\).*/\\1/'").decode()
    azuna.run(f"ip route add {server_ip} via {default_gw}")
    azuna.run(f"ip route add 0/1 dev {dev_name}")
    azuna.run(f"ip route add 128/1 dev {dev_name}")
    
    logger.info("setup iptables")
    azuna.run(f"iptables -t nat -A POSTROUTING -o {dev_name} -j MASQUERADE")
    azuna.run(f"iptables -I FORWARD 1 -i {dev_name} -m state --state RELATED,ESTABLISHED -j ACCEPT")
    azuna.run(f"iptables -I FORWARD 1 -o {dev_name} -j ACCEPT")

    logger.info("start forwarding")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    azuna.loop(t, s, mtu=mtu, address=address, logger=logger)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        logger.error(f"failed to forward data: {e}\n{traceback.format_exc()}")
        exit(-1)
