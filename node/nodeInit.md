# 1 搭建环境预览
| 软件 | 版本 | 备注 |
| :------: | :------: |:------: |
| docker | 18.06.3-ce |  |
| ubuntu | ubuntu-18.04.3-desktop-amd64 |  |
| docker-compose | 1.24.1 |  |
| kubectl | 1.15.6 |  |
| helm | 2.16.0 |  |

# 2 配置服务器（所有服务器建议使用root用户）

## 2.1 主机配置(可能需要root用户来配置)
### 2.1.1 主机名配置
主机名只支持包含 - 和 .(中横线和点)两种特殊符号，并且主机名不能出现重复。
```shell
hostnamectl --static set-hostname  rk1
hostnamectl --static set-hostname  rk2
```

### 2.1.2 主机名配置
配置每台主机的hosts(/etc/hosts),添加host_ip $hostname到/etc/hosts文件中。
```shell
sudo cat >> /etc/hosts <<EOF
192.168.15.130 rk1
192.168.15.131 rk2
EOF
```

### 2.1.3 关闭swap
```shell
swapoff -a
yes | cp /etc/fstab /etc/fstab_bak
cat /etc/fstab_bak |grep -v swap > /etc/fstab
cat /etc/fstab
```

### 2.1.4 关闭防火墙
ufw disable

### 2.1.5 配置时区 语言
查看时区
```shell
date -R或者timedatectl
```

修改时区
```shell
sudo rm -f /etc/localtime
sudo touch /etc/localtime
sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo 'Asia/Shanghai' >/etc/timezone
```

修改系统语言环境(可选)
```shell
sudo echo 'LANG="en_US.UTF-8"' >> /etc/profile;source /etc/profile
```

### 2.1.6 配置DNS
对于类似Ubuntu 18这类默认使用systemd-resolve管理DNS的系统，建议禁用systemd-resolved服务，然后手动配置DNS。

#### 2.1.6.1 方案一
```shell
sudo rm /etc/resolv.conf
sudo ln -s /var/run/systemd/resolve/resolv.conf /etc/resolv.conf
```

#### 2.1.6.2 方案二

##### (1)禁用systemd-resolved.service
```shell
systemctl disable systemd-resolved.service
systemctl stop systemd-resolved.service
rm -rf /etc/resolv.conf
touch /etc/resolv.conf
```

##### (2)接着编辑/etc/resolv.conf添加DNS服务器 (参考/var/run/systemd/resolve/resolv.conf)
10.6.0.21  需要修改
```shell
# 格式
nameserver //定义DNS服务器的IP地址
domain //定义本地域名
search //定义域名的搜索列表
sortlist //对返回的域名进行排序

# 示例
domain cypass.com
search www.cypass.com cypass.com
nameserver 10.6.0.21
nameserver 8.8.8.8
```

##### (3)重启systemd-resolved.service
```shell
systemctl enable systemd-resolved.service
systemctl start systemd-resolved.service
```

### 2.1.7 Kernel性能调优
```shell
cat >> /etc/sysctl.conf<<EOF
net.bridge.bridge-nf-call-ip6tables=1
net.bridge.bridge-nf-call-iptables=1
net.ipv4.ip_forward=1
net.ipv4.conf.all.forwarding=1
net.ipv4.neigh.default.gc_thresh1=4096
net.ipv4.neigh.default.gc_thresh2=6144
net.ipv4.neigh.default.gc_thresh3=8192
net.ipv4.neigh.default.gc_interval=60
net.ipv4.neigh.default.gc_stale_time=120
EOF
sysctl -p

#nofile
cat >> /etc/security/limits.conf <<EOF
* soft nofile 65535
* hard nofile 65536
EOF
```

### 2.1.8 内核模块(可选)
模块查询: lsmod | grep <模块名>
模块加载: modprobe <模块名>
```shell
mkdir -p /etc/sysconfig/modules/
touch /etc/sysconfig/modules/ipvs.modules
cat > /etc/sysconfig/modules/ipvs.modules <<EOF
#!/bin/bash
ipvs_modules="ip_vs ip_vs_lc ip_vs_wlc ip_vs_rr ip_vs_wrr ip_vs_lblc ip_vs_lblcr ip_vs_dh ip_vs_sh ip_vs_fo ip_vs_nq ip_vs_sed ip_vs_ftp nf_conntrack iptable_filter iptable_nat iptable_mangle iptable_raw nf_conntrack_netlink nf_conntrack nf_conntrack_ipv4 nf_defrag_ipv4 nf_nat nf_nat_ipv4 nf_nat_masquerade_ipv4 nfnetlink udp_tunnel veth vxlan x_tables xt_addrtype xt_conntrack xt_comment xt_mark xt_multiport xt_nat xt_recent xt_set xt_statistic xt_tcpudp "
for kernel_module in \${ipvs_modules}; do
/sbin/modinfo -F filename \${kernel_module} > /dev/null 2>&1
if [ $? -eq 0 ]; then
/sbin/modprobe \${kernel_module}
fi
done
EOF
chmod 755 /etc/sysconfig/modules/ipvs.modules && bash /etc/sysconfig/modules/ipvs.modules && lsmod | grep ip_vs
```

## 2.2 Docker安装
### 2.2.1 修改系统源
UBUNTU 18.04.X
```shell
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak
cat > /etc/apt/sources.list << EOF
deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
EOF
```

### 2.2.2 安装docker-ce
用作rancher的ha服务器
```shell
# 定义用户名
NEW_USER=rancher
# 添加用户(可选)
sudo adduser rancher
# 为新用户设置密码
sudo passwd $NEW_USER
# 为新用户添加sudo权限
sudo echo "$NEW_USER  ALL=(ALL:ALL) ALL" >> /etc/sudoers
# 定义安装版本
export docker_version=18.06.3;
# step 1: 安装必要的一些系统工具
sudo apt-get remove docker docker-engine docker.io containerd runc -y;
sudo apt-get update;
sudo apt-get -y install apt-transport-https ca-certificates \
curl software-properties-common bash-completion gnupg-agent;
# step 2: 安装GPG证书
sudo curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | \
sudo apt-key add -;
# Step 3: 写入软件源信息
sudo add-apt-repository "deb [arch=amd64] http://mirrors.aliyun.com/docker-ce/linux/ubuntu \
$(lsb_release -cs) stable";
# Step 4: 更新并安装 Docker-CE
sudo apt-get -y update;
version=$(apt-cache madison docker-ce|grep ${docker_version}|awk '{print $3}');
echo $version
# --allow-downgrades 允许降级安装
sudo apt-get -y install docker-ce=${version} --allow-downgrades;
# 把当前用户加入docker组
sudo usermod -aG docker $NEW_USER;
sudo usermod -aG root $NEW_USER;
# 设置开机启动
sudo systemctl enable docker;
# 切换用户
sudo su rancher
```

### 2.2.3 安装docker-compose
```shell
wget https://github.com/docker/compose/releases/download/1.24.0/docker-compose-Linux-x86_64 

mv docker-compose-Linux-x86_64 /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose
```
    
### 2.2.4 docker配置 (一下配置都是可选，酌情调整)  
文件位置/etc/docker/daemon.json (如果没有请添加)
#### (1) 配置insecure-registries私有仓库(可选)
```shell
touch /etc/docker/daemon.json
cat >>/etc/docker/daemon.json<<EOF
{
    "insecure-registries": ["registry.cyai.com"]
}
EOF
```
#### (2) 配置镜像下载和上传并发数(可选)
从Docker1.12开始，支持自定义下载和上传镜像的并发数，默认值上传为3个并发，下载为5个并发。通过添加”max-concurrent-downloads”和”max-concurrent-uploads”参数对其修改:
```shell
{
    "max-concurrent-downloads": 3,
    "max-concurrent-uploads": 5
}
```
#### (3) 配置镜像加速地址(可选)
```shell
{
    "registry-mirrors": ["https://7bezldxe.mirror.aliyuncs.com/","https://IP:PORT/"]
}
```
#### (4) 配置Docker存储驱动(可选)
```shell
{
    "storage-driver": "overlay2",
    "storage-opts": ["overlay2.override_kernel_check=true"]
}
```
#### (5) 配置日志驱动(可选)
容器在运行时会产生大量日志文件，很容易占满磁盘空间。通过配置日志驱动来限制文件大小与文件的数量。 >限制单个日志文件为100M,最多产生3个日志文件
```shell
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    }
}
```
#### (6)Ubuntu\Debian系统 ，docker info提示WARNING: No swap limit support
Ubuntu\Debian系统下，默认cgroups未开启swap account功能，这样会导致设置容器内存或者swap资源限制不生效。可以通过以下命令解决:
```shell
# 统一网卡名称为ethx
sudo sed -i 's/en[[:alnum:]]*/eth0/g' /etc/network/interfaces;
sudo sed -i 's/GRUB_CMDLINE_LINUX="\(.*\)"/GRUB_CMDLINE_LINUX="net.ifnames=0 cgroup_enable=memory swapaccount=1 biosdevname=0 \1"/g' /etc/default/grub;
sudo update-grub;
```

### 2.2.5 安装kubectl(可选)
```shell
wget https://www.rancher.cn/download/kubernetes/linux-amd64-v1.15.6-kubectl
mv linux-amd64-v1.15.6-kubectl /usr/bin/kubectl
chmod +x /usr/bin/kubectl

# 临时设置
source <(kubectl completion bash)
```
### 2.2.6 安装helm(可选)
```shell
wget https://get.helm.sh/helm-v2.16.0-linux-amd64.tar.gz
tar -xvf helm-v2.16.0-linux-amd64.tar.gz
mv linux-amd64/helm /usr/bin/helm

# 临时设置
source <(helm completion bash)
```


## 2.3 配置命令补全(可选)
```shell
# 临时设置
source <(helm completion bash)
source <(kubectl completion bash)

#永久设置方法
cat >> /root/.bashrc <<EOF
source <(helm completion bash)
source <(kubectl completion bash)
EOF
source /root/.bashrc
```

## 2.4 重启服务器
```shell
reboot
```
