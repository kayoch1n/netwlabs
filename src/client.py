import azuna
import subprocess
import traceback

logger = azuna.get_logger(__file__)

def main():
    import socket
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', required=True)
    parser.add_argument('-p', '--port', required=True, type=int)
    parser.add_argument('--dev_name', default='yu0')
    parser.add_argument('--dev_if_addr', default='10.8.0.2/16')

    args = parser.parse_args()
    
    address = socket.getaddrinfo(args.server, args.port)[0][-1]
    server_ip, _ = address

    dev_name, dev_if_addr = args.dev_name, args.dev_if_addr
    logger.info("create device %s", dev_name)
    t, mtu = azuna.create_tun(name=dev_name, if_addr=dev_if_addr)
    
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
    except subprocess.CalledProcessError as e:
        logger.error(f"{traceback.format_exc()}\nstdout:{e.stdout}\nstderr:{e.stderr}")
        exit(-1)
    except Exception as e:

        logger.error(f"failed to forward data: {e}\n{traceback.format_exc()}")
        exit(-1)
