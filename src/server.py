import azuna
logger = azuna.get_logger(__file__)


def main():

    import socket
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--listen', default='0.0.0.0')
    parser.add_argument('-p', '--port', required=True, type=int)
    parser.add_argument('--dev_name', default='yu0')

    args = parser.parse_args()

    dev_name = args.dev_name
    t, mtu = azuna.create_tun(dev_name=dev_name, if_addr='10.8.0.1/16')

    logger.info("setup iptables")
    azuna.run(f"iptables -t nat -A POSTROUTING -s 10.8.0.1/16 ! -d 10.8.0.1/16 -m comment --comment azuna -j MASQUERADE")
    azuna.run(f'iptables -A FORWARD -s 10.8.0.1/16 -m state --state RELATED,ESTABLISHED -j ACCEPT')
    azuna.run(f'iptables -A FORWARD -d 10.8.0.1/16 -j ACCEPT')

    logger.info("start forwarding")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.bind((args.listen, args.port))
    azuna.loop(t, s, mtu=mtu, logger=logger)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        logger.error(f"failed to forward data: {e}\n{traceback.format_exc()}")
        exit(-1)
