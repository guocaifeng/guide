# Harbor HA安装

## 一、说明
本文档基于Harbor1.8.2版本，它不适用于1.8.0之前的版本。本指南仅供参考。

192.168.15.128 reg.cyai.com		harbor1
192.168.15.136 reg.cyai.com		harbor2

192.168.15.137 					nginx

## 二、Harbor高可用性介绍
本文档介绍了实现高可用系统的一些常用方法，重点是核心Harbor服务和与Harbor密切配合的其他开源服务。您需要解决在运行的Harbor环境中，所有应用程序软件的高可用性问题。重要的是确保您的服务冗余且可用。

### 1、无状态服务
要使无状态服务具有高可用性，您需要提供实例冗余并对其进行负载平衡。无状态的Harbor服务包括：
```java
nginx
harbor-portal
harbor-jobservice
harbor-core
registryctl
registry
clair
harbor-log
```
### 2、有状态的服务
有状态服务更难管理,提供额外的实例和负载平衡并不能解决问题。有状态的Harbor服务包括以下服务：
```java
harbor-db
redis
```

## 三、HA架构(主主复制)

如上图所示，架构中涉及的组件包括：

**VIP**：虚拟IP，Harbour用户将通过此虚拟IP地址访问Harbor。此VIP地址仅在一个负载均衡器节点上激活。如果活动负载均衡器节点关闭，它将自动切换到另一个节点。

**LoadBalancer 01和02**：它们一起组成一个组，避免负载均衡器节点的单点故障。Keepalived安装在两个负载均衡器节点上。两个Keepalived实例将组成一个VRRP组来提供VIP，并确保同一时间VIP仅在一个节点上被配置。Keepalived中的LVS组件负责根据路由算法平衡不同Harbor服务器之间的请求。

**Harbor服务器1..n**：这些是正在运行的Harbor实例。它们处于主动-主动模式。用户可以根据工作量设置多个节点。



## 四、HA安装
### 1、负载平衡器设置
**使用软件负载均衡器keepalived直接来代理**
#### 3.1 Loadbalancer01
##### (1) 安装keepalived curl
```shell
apt-get install keepalived curl
```
##### (2) 配置keepalived
/etc/keepalived/keepalived.conf

您需要将更改为您的 change_to_VIP_address 地址(有两个地方)；
将harbor_node1_IP(两个地方)和harbour_node2_IP(两个地方)更改为真实Harbor节点IP；
ens160 需要更改为对应的网卡
如果您有两个以上的节点，请在keepalived.conf中添加更多real_server定义；

```shell
global_defs {
  router_id rk1
}
#vrrp_sync_groups VG1 {
#  group {
#    VI_1
#  }
#}

#Please change "ens160" to the interface name on you loadbalancer hosts.
#In some case it will be eth0, ens16xxx etc.
vrrp_instance VI_1 {
  interface ens33
  track_interface {
    ens33
  }
  state MASTER
  virtual_router_id 51
  priority 20
  virtual_ipaddress {
    192.168.15.200
  }
  advert_int 1
  authentication {
    auth_type PASS
    auth_pass d0cker
  }
}

virtual_server 192.168.15.200 80 {
  delay_loop 15
  lb_algo rr
  lb_kind NAT
  protocol TCP
  persistence_timeout 10
  real_server 192.168.15.131 80 {
    weight 10
    MISC_CHECK {
        misc_path "/usr/local/bin/check.sh 192.168.15.131:80"
        misc_timeout 5
    }
  }
#  real_server 192.168.15.132 80 {
#    weight 10
#    MISC_CHECK {
#        misc_path "/usr/local/bin/check.sh 192.168.15.132:80"
#        misc_timeout 5
#    }
#  }
}
#########################End of HTTP############################
##########################HTTPS#################################
#Please uncomment the follow when harbor running under https
#virtual_server <change_to_VIP_address> 443 {
#  delay_loop 15
#  lb_algo rr
#  lb_kind NAT
#  protocol TCP
#  nat_mask 255.255.255.0
#  persistence_timeout 10
#
#  real_server <harbor_node1_ip> 443 {
#    weight 10
#    MISC_CHECK {
#       misc_path "/usr/local/bin/check.sh <harbor_node1_ip>"
#       misc_timeout 5
#    }
#  }
#
#  real_server harbor_node2_ip 443 {
#    weight 10
#    MISC_CHECK {
#       misc_path "/usr/local/bin/check.sh <harbor_node2_ip>"
#       misc_timeout 5
#    }
#  }
#}
#########################End of HTTPS Section#################

```
##### (3) 配置运行状况检查

将服务器运行状况检查脚本保存到/usr/local/bin/check.sh
```shell
#!/bin/bash

set -e
#get protocol

LOG=/var/log/keepalived_check.log
nodeip=$1
nodeaddress="http://${nodeip}"
http_code=`curl -s -o /dev/null -w "%{http_code}" ${nodeaddress}`

if [ $http_code == 200 ] ; then
  protocol="http"
elif [ $http_code == 301 ]
then
  protocol="https"
else
#  echo "`date +"%Y-%m-%d %H:%M:%S"` $1, CHECK_CODE=$http_code" >> $LOG
  exit 1
fi

systeminfo=`curl -k -o - -s ${protocol}://${nodeip}/api/systeminfo`

echo $systeminfo | grep "registry_url"
if [ $? != 0 ] ; then
  exit 1
fi
#TODO need to check Clair, but currently Clair status api is unreachable from LB.
# echo $systeminfo | grep "with_clair" | grep "true"
# if [ $? == 0 ] ; then
# clair is enabled
# do some clair check
# else
# clair is disabled
# fi

#check top api

http_code=`curl -k -s -o /dev/null -w "%{http_code}\n" ${protocol}://${nodeip}/api/repositories/top`
set +e
if [ $http_code == 200 ] ; then
  exit 0
else
  exit 1
fi
```
运行以下命令以添加执行权限。
```shell
chmod +x /usr/local/bin/check.sh
```

##### (5) 重新启动Keepalived服务
```shell
systemctl restart keepalived
```
#### 3.2 Loadbalancer02
按照与Loadbalancer01列表相同的步骤1到5进行部署
需要更改的位置：/etc/keepalived/keepalived.conf
```shell
global_defs {
  router_id rk2
}
#vrrp_sync_groups VG1 {
#  group {
#    VI_1
#  }
#}

#Please change "ens160" to the interface name on you loadbalancer hosts.
#In some case it will be eth0, ens16xxx etc.
vrrp_instance VI_1 {
  interface ens33
  track_interface {
    ens33
  }
  state BACKUP
  virtual_router_id 51
  priority 10
  virtual_ipaddress {
    192.168.15.200
  }
  advert_int 1
  authentication {
    auth_type PASS
    auth_pass d0cker
  }
}

virtual_server 192.168.15.200 80 {
  delay_loop 15
  lb_algo rr
  lb_kind NAT
  protocol TCP
  persistence_timeout 10
  
#  real_server 192.168.15.131 80 {
#    weight 10
#    MISC_CHECK {
#        misc_path "/usr/local/bin/check.sh 192.168.15.131:80"
#        misc_timeout 5
#    }
#  }
  real_server 192.168.15.132 80 {
    weight 10
    MISC_CHECK {
        misc_path "/usr/local/bin/check.sh 192.168.15.132:80"
        misc_timeout 5
    }
  }
}
#########################End of HTTP############################
##########################HTTPS#################################
#Please uncomment the follow when harbor running under https
#virtual_server <change_to_VIP_address> 443 {
#  delay_loop 15
#  lb_algo rr
#  lb_kind NAT
#  protocol TCP
#  nat_mask 255.255.255.0
#  persistence_timeout 10
#
#  real_server <harbor_node1_ip> 443 {
#    weight 10
#    MISC_CHECK {
#       misc_path "/usr/local/bin/check.sh <harbor_node1_ip>"
#       misc_timeout 5
#    }
#  }
#
#  real_server harbor_node2_ip 443 {
#    weight 10
#    MISC_CHECK {
#       misc_path "/usr/local/bin/check.sh <harbor_node2_ip>"
#       misc_timeout 5
#    }
#  }
#}
#########################End of HTTPS Section#################

```
------------


### 4、Harbor节点 1 设置
#### 4.1 从互联网下载离线安装包
https://storage.googleapis.com/harbor-releases/release-1.8.0/harbor-offline-installer-v1.8.2.tgz
#### 4.2 拷贝到服务器解压拷贝到服务器解压
```shell
root@ubuntu:~/habor# tar -xvf harbor-offline-installer-v1.8.2.tgz 
root@ubuntu:~/habor# cd harbor/
root@ubuntu:~/habor/harbor# ls
harbor.v1.8.2.tar.gz  harbor.yml  install.sh  LICENSE  prepare

创建目录结构：
mkdir -p /data

导入镜像：
root@ubuntu:~/habor/harbor# docker load -i harbor.v1.8.2.tar.gz

创建daemon.json
cat >> /etc/docker/daemon.json<<EOF
{
	"insecure-registries": ["reg.cyai.com"]
}
EOF

```
#### 4.3 修改harbor.yaml文件
**仅需要修改redis和postgres的地址等信息**
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

#### 4.4 生成环境变量
##### (1)生成环境变量
./prepare --with-clair
##### (2)修改docker-compose.yaml文件
如果当前节点是128 那么需要下边需要修改为136
reg.cyai.com:192.168.15.136

```shell
version: '2.3'
services:
  log:
    image: goharbor/harbor-log:v1.8.2
    container_name: harbor-log
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    dns_search: .
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - DAC_OVERRIDE
      - SETGID
      - SETUID
    volumes:
      - /var/log/harbor/:/var/log/docker/:z
      - ./common/config/log/:/etc/logrotate.d/:z
    ports:
      - 127.0.0.1:1514:10514
    networks:
      - harbor
  registry:
    image: goharbor/registry-photon:v2.7.1-patch-2819-v1.8.2
    container_name: registry
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    volumes:
      - /data/registry:/storage:z
      - ./common/config/registry/:/etc/registry/:z
      - type: bind
        source: /data/secret/registry/root.crt
        target: /etc/registry/root.crt
    networks:
      - harbor
      - harbor-clair
    dns_search: .
    depends_on:
      - log
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "registry"
  registryctl:
    image: goharbor/harbor-registryctl:v1.8.2
    container_name: registryctl
    env_file:
      - ./common/config/registryctl/env
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    volumes:
      - /data/registry:/storage:z
      - ./common/config/registry/:/etc/registry/:z
      - type: bind
        source: ./common/config/registryctl/config.yml
        target: /etc/registryctl/config.yml
    networks:
      - harbor
    dns_search: .
    depends_on:
      - log
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "registryctl"
  postgresql:
    image: goharbor/harbor-db:v1.8.2
    container_name: harbor-db
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - DAC_OVERRIDE
      - SETGID
      - SETUID
    volumes:
      - /data/database:/var/lib/postgresql/data:z
    networks:
      harbor:
      harbor-clair:
        aliases:
          - harbor-db
    dns_search: .
    env_file:
      - ./common/config/db/env
    depends_on:
      - log
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "postgresql"
  core:
    image: goharbor/harbor-core:v1.8.2
    container_name: harbor-core
    env_file:
      - ./common/config/core/env
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID
    volumes:
      - /data/ca_download/:/etc/core/ca/:z
      - /data/psc/:/etc/core/token/:z
      - /data/:/data/:z
      - ./common/config/core/certificates/:/etc/core/certificates/:z
      - type: bind
        source: ./common/config/core/app.conf
        target: /etc/core/app.conf
      - type: bind
        source: /data/secret/core/private_key.pem
        target: /etc/core/private_key.pem
      - type: bind
        source: /data/secret/keys/secretkey
        target: /etc/core/key
    networks:
      harbor:
      harbor-clair:
        aliases:
          - harbor-core
    dns_search: .
    depends_on:
      - log
      - registry
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "core"
  portal:
    image: goharbor/harbor-portal:v1.8.2
    container_name: harbor-portal
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - NET_BIND_SERVICE
    networks:
      - harbor
    dns_search: .
    depends_on:
      - log
      - core
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "portal"

  jobservice:
    image: goharbor/harbor-jobservice:v1.8.2
    container_name: harbor-jobservice
    env_file:
      - ./common/config/jobservice/env
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    volumes:
      - /data/job_logs:/var/log/jobs:z
      - type: bind
        source: ./common/config/jobservice/config.yml
        target: /etc/jobservice/config.yml
    networks:
      - harbor
      - harbor-clair
    dns_search: .
    depends_on:
      - redis
      - core
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "jobservice"
  redis:
    image: goharbor/redis-photon:v1.8.2
    container_name: redis
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    volumes:
      - /data/redis:/var/lib/redis
    networks:
      harbor:
    dns_search: .
    depends_on:
      - log
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "redis"
  proxy:
    image: goharbor/nginx-photon:v1.8.2
    container_name: nginx
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - NET_BIND_SERVICE
    volumes:
      - ./common/config/nginx:/etc/nginx:z
    networks:
      - harbor
    dns_search: .
    ports:
      - 80:80
    depends_on:
      - postgresql
      - registry
      - core
      - portal
      - log
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "proxy"
  clair:
    networks:
      - harbor-clair
    container_name: clair
    image: goharbor/clair-photon:v2.0.8-v1.8.2
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.136"
    cap_drop:
      - ALL
    cap_add:
      - DAC_OVERRIDE
      - SETGID
      - SETUID
    cpu_quota: 50000
    dns_search: .
    depends_on:
      - postgresql
    volumes:
      - type: bind
        source: ./common/config/clair/config.yaml
        target: /etc/clair/config.yaml
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "clair"
    env_file:
      ./common/config/clair/clair_env
networks:
  harbor:
    external: false
  harbor-clair:
    external: false

```

### 5 Harbor节点2部署
#### 5.1 copy节点1的如下内容
```shell
-rw-r--r-- 1 root root 578167000 Oct 15 10:04 harbor.v1.8.2.tar.gz
-rw-r--r-- 1 root root      4253 Oct 15 17:02 harbor.yml
-rwxr-xr-x 1 root root      1654 Oct 15 10:03 prepare
```
#### 5.2 服务器配置

创建目录结构：
```shell
mkdir -p /data
```
准备环境变量：
```shell
./prepare --with-clair
```
导入镜像：
```shell
root@ubuntu:~/habor/harbor# docker load -i harbor.v1.8.2.tar.gz
```
创建daemon.json
```shell
cat >> /etc/docker/daemon.json<<EOF
{
    "insecure-registries": ["reg.cyai.com"]
}
EOF
```
重启docker
```shell
systemctl restart docker
```
编辑docker-compose.yaml文件
```shell
cd /root/harbor/
cat >> docker-compose.yml <<EOF
version: '2.3'
services:
  log:
    image: goharbor/harbor-log:v1.8.2
    container_name: harbor-log
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    dns_search: .
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - DAC_OVERRIDE
      - SETGID
      - SETUID
    volumes:
      - /var/log/harbor/:/var/log/docker/:z
      - ./common/config/log/:/etc/logrotate.d/:z
    ports:
      - 127.0.0.1:1514:10514
    networks:
      - harbor
  registry:
    image: goharbor/registry-photon:v2.7.1-patch-2819-v1.8.2
    container_name: registry
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    volumes:
      - /data/registry:/storage:z
      - ./common/config/registry/:/etc/registry/:z
      - type: bind
        source: /data/secret/registry/root.crt
        target: /etc/registry/root.crt
    networks:
      - harbor
      - harbor-clair
    dns_search: .
    depends_on:
      - log
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "registry"
  registryctl:
    image: goharbor/harbor-registryctl:v1.8.2
    container_name: registryctl
    env_file:
      - ./common/config/registryctl/env
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    volumes:
      - /data/registry:/storage:z
      - ./common/config/registry/:/etc/registry/:z
      - type: bind
        source: ./common/config/registryctl/config.yml
        target: /etc/registryctl/config.yml
    networks:
      - harbor
    dns_search: .
    depends_on:
      - log
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "registryctl"
  postgresql:
    image: goharbor/harbor-db:v1.8.2
    container_name: harbor-db
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - DAC_OVERRIDE
      - SETGID
      - SETUID
    volumes:
      - /data/database:/var/lib/postgresql/data:z
    networks:
      harbor:
      harbor-clair:
        aliases:
          - harbor-db
    dns_search: .
    env_file:
      - ./common/config/db/env
    depends_on:
      - log
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "postgresql"
  core:
    image: goharbor/harbor-core:v1.8.2
    container_name: harbor-core
    env_file:
      - ./common/config/core/env
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID
    volumes:
      - /data/ca_download/:/etc/core/ca/:z
      - /data/psc/:/etc/core/token/:z
      - /data/:/data/:z
      - ./common/config/core/certificates/:/etc/core/certificates/:z
      - type: bind
        source: ./common/config/core/app.conf
        target: /etc/core/app.conf
      - type: bind
        source: /data/secret/core/private_key.pem
        target: /etc/core/private_key.pem
      - type: bind
        source: /data/secret/keys/secretkey
        target: /etc/core/key
    networks:
      harbor:
      harbor-clair:
        aliases:
          - harbor-core
    dns_search: .
    depends_on:
      - log
      - registry
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "core"
  portal:
    image: goharbor/harbor-portal:v1.8.2
    container_name: harbor-portal
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - NET_BIND_SERVICE
    networks:
      - harbor
    dns_search: .
    depends_on:
      - log
      - core
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "portal"

  jobservice:
    image: goharbor/harbor-jobservice:v1.8.2
    container_name: harbor-jobservice
    env_file:
      - ./common/config/jobservice/env
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    volumes:
      - /data/job_logs:/var/log/jobs:z
      - type: bind
        source: ./common/config/jobservice/config.yml
        target: /etc/jobservice/config.yml
    networks:
      - harbor
      - harbor-clair
    dns_search: .
    depends_on:
      - redis
      - core
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "jobservice"
  redis:
    image: goharbor/redis-photon:v1.8.2
    container_name: redis
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    volumes:
      - /data/redis:/var/lib/redis
    networks:
      harbor:
    dns_search: .
    depends_on:
      - log
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "redis"
  proxy:
    image: goharbor/nginx-photon:v1.8.2
    container_name: nginx
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - NET_BIND_SERVICE
    volumes:
      - ./common/config/nginx:/etc/nginx:z
    networks:
      - harbor
    dns_search: .
    ports:
      - 80:80
    depends_on:
      - postgresql
      - registry
      - core
      - portal
      - log
    logging:
      driver: "syslog"
      options:  
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "proxy"
  clair:
    networks:
      - harbor-clair
    container_name: clair
    image: goharbor/clair-photon:v2.0.8-v1.8.2
    restart: always
    extra_hosts:
      - "reg.cyai.com:192.168.15.128"
    cap_drop:
      - ALL
    cap_add:
      - DAC_OVERRIDE
      - SETGID
      - SETUID
    cpu_quota: 50000
    dns_search: .
    depends_on:
      - postgresql
    volumes:
      - type: bind
        source: ./common/config/clair/config.yaml
        target: /etc/clair/config.yaml
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://127.0.0.1:1514"
        tag: "clair"
    env_file:
      ./common/config/clair/clair_env
networks:
  harbor:
    external: false
  harbor-clair:
    external: false
EOF
```
启动
```shell
docker-compose up -d
```


### 6 登录
```shell
登录账号密码
admin
admin
```

