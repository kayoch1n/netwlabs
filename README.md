# VPN demo

仅用于学习 tun 设备原理，根据[这篇文章](https://lxd.me/a-simple-vpn-tunnel-with-tun-device-demo-and-some-basic-concepts)的代码、用 Python 改写而成。详情见我的[笔记](https://kayoch1n.github.io/blog/linux-tuntap/)。


## Run in docker container

```bash
# 构建镜像
docker build -t nijigasaki:3 .
# 拉起来容器
make upd
# 关闭容器
make down
# 进入 client
make setsuna
# 进入 server
make shizuku
```