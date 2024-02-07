# VPN demo

仅用于学习 tun 设备原理。

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