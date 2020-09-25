# Harbor 单点安装

## 1 说明
本文档基于Harbor1.8.2版本。本指南仅供参考。

192.168.15.128 reg.cyai.com		harbor

## 2 Harbor节点设置
### 2.1 从互联网下载离线安装包

https://storage.googleapis.com/harbor-releases/release-1.8.0/harbor-offline-installer-v1.8.2.tgz

### 2.2 拷贝到服务器解压拷贝到服务器解压
```shell
root@ubuntu:~/habor# tar -xvf harbor-offline-installer-v1.8.2.tgz 
root@ubuntu:~/habor# cd harbor/
root@ubuntu:~/habor/harbor# ls
harbor.v1.8.2.tar.gz  harbor.yml  install.sh  LICENSE  prepare

导入镜像：
root@ubuntu:~/habor/harbor# docker load -i harbor.v1.8.2.tar.gz

创建daemon.json
cat >> /etc/docker/daemon.json<<EOF
{
	"insecure-registries": ["reg.cyai.com"]
}
EOF

```
### 2.3 修改harbor.yaml文件
reg.cyai.com  一下配置中，仅需要修改域名即可。其他配置看情况调整
```shell
# 配置当前服务器域名
hostname: reg.cyai.com
http:
  port: 80
# Harbor仓库登录密码  账号默认admin 
harbor_admin_password: admin
database:
  password: root123

# registry仓库镜像实际存储路径
data_volume: /data

clair:
  updaters_interval: 12
  no_proxy: 127.0.0.1,localhost,core,registry
jobservice:
  max_job_workers: 10
log:
  level: info
  rotate_count: 50
  rotate_size: 200M
  location: /var/log/harbor
_version: 1.8.2
```

### 2.4 生成环境变量
```shell
./prepare --with-clair
```

### 2.5 启动环境变量
启动
```shell
docker-compose up -d
```

### 2.6 登录
```shell
登录账号密码
admin
admin
```

