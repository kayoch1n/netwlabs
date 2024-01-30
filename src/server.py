import azuna
import subprocess
import traceback

logger = azuna.get_logger(__file__)


def main():

    import socket
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--listen', default='0.0.0.0')
    parser.add_argument('-p', '--port', required=True, type=int)
    parser.add_argument('--dev_name', default='yu0')
    parser.add_argument('--dev_if_addr', default='10.8.0.1/16')

    args = parser.parse_args()

    dev_name, dev_if_addr = args.dev_name, args.dev_if_addr
    logger.info("create device %s", dev_name)
    t, mtu = azuna.create_tun(name=dev_name, if_addr=dev_if_addr)

    logger.info("setup iptables")
    # nat POSTROUTING 不能通过 -i 去 match
    azuna.run(f"iptables -t nat -A POSTROUTING -s {dev_if_addr} ! -d {dev_if_addr} -j MASQUERADE")
    # 也可以用 IP 地址
    azuna.run(f'iptables -A FORWARD -i {dev_name} -m state --state RELATED,ESTABLISHED -j ACCEPT')
    azuna.run(f'iptables -A FORWARD -o {dev_name} -j ACCEPT')

    logger.info("start forwarding")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.bind((args.listen, args.port))
    azuna.loop(t, s, mtu=mtu, logger=logger)

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        logger.error(f"{traceback.format_exc()}\nstdout:{e.stdout}\nstderr:{e.stderr}")
        exit(-1)
    except Exception as e:

        logger.error(f"{e}\n{traceback.format_exc()}")
        exit(-1)
