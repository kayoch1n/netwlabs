import socket
import logging

IFF_TUN = 0x0001
IFF_NO_PI = 0x1000
TUNSETIFF = 0x400454ca

def create_tun(if_addr, name):
    import struct
    import fcntl
    import re

    f = open("/dev/net/tun", buffering=0, mode='r+b')
    
    bs = struct.pack("16sH", name.encode(), IFF_TUN|IFF_NO_PI)
    fcntl.ioctl(f, TUNSETIFF, bs, False)

    output = run(f'ip link show dev {name}').decode()
    m = re.search(output, r'mtu ([0-9]+)')
    try:
        mtu = m.group(1)
    except:
        mtu = '1500'

    run(f'ip addr add {if_addr} dev {name}')
    run(f'ip link set dev {name} up')
    return f, int(mtu)

def encrypt(data: bytes):
    # return bytes(b^0xff for b in data)
    return data

decrypt = encrypt

def get_logger(name):
    import sys

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(f'{name}.log', mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    return logger


def loop(f, s: socket.socket, mtu=1500, logger=None, address=None):
    import select
    from contextlib import closing

    if not logger:
        logger = logging

    s.setblocking(False)

    with f as f, closing(s) as s:
        while True:
            rs, [], [] = select.select([f, s], [], [])
            if f in rs:
                data = f.read(mtu)
                s.sendto(encrypt(data), address)
                logger.debug("%d byte(s) sent to %s", len(data), address)
        
            if s in rs:
                data, address = s.recvfrom(mtu)
                logger.info("%d byte(s) received from %s", len(data), address)
                f.write(decrypt(data))

def run(cmd):
    import subprocess
    
    if isinstance(cmd, str):
        cmd = ['sh', '-c', cmd]

    return subprocess.run(cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE).stdout
