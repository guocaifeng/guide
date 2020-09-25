# 1 安装rke和kubectl(所有服务器安装)
## 1.1 二进制文件安装
```shell
### 安装rke
wget https://github.com/rancher/rke/releases/download/v0.3.2/rke_linux-amd64
chmod +x rke_linux-amd64
su root
mv rke_linux-amd64 /usr/local/bin/rke
rke --version

### 安装rke
wget https://www.rancher.cn/download/kubernetes/linux-amd64-v1.15.5-kubectl
chmod +x linux-amd64-v1.15.5-kubectl
su root
mv linux-amd64-v1.15.5-kubectl /usr/local/bin/kubectl
kubectl --version
```
# 2 安装kubernetes集群(128服务器操作)
## 2.1 编写rancher-cluster.yaml文件
详细配置文件请查看 https://www.rancher.cn/docs/rke/latest/cn/config-options/
一下配置为简要配置信息(用作初始化k8s集群使用)
```shell
nodes:
  - address: 192.168.15.128
    user: rancher
    hostname_override: rk1
    role:
      - controlplane
      - etcd
      - worker
    ssh_key_path: /home/rancher/.ssh/id_rsa
    port: 22
  - address: 192.168.15.136
    user: rancher
    hostname_override: rk2
    role:
      - controlplane
      - etcd
      - worker
    ssh_key_path: /home/rancher/.ssh/id_rsa
    port: 22
  - address: 192.168.15.137
    user: rancher
    hostname_override: rk3
    role:
      - controlplane
      - etcd
      - worker
    ssh_key_path: /home/rancher/.ssh/id_rsa
    port: 22

cluster_name: rancher-cyai

services:
  etcd:
    backup_config:
      enabled: true
      interval_hours: 12
      retention: 6
```

## 2.2 启动
```shell
# 启动
rke up --config rancher-cluster.yaml
# 验证
kubectl --kubeconfig=kube_config_rancher-cluster.yaml get nodes

# 如果失败请使用如下命令清理服务器
rke remove --config rancher-cluster.yaml
```

## 2.3 kube配置文件
```shell
# 将yaml文件放到.kube中
cp kube_config_rancher-cluster.yaml .kube/config
# 验证
$ kubectl get po --all-namespaces
NAMESPACE       NAME                                      READY   STATUS      RESTARTS   AGE
ingress-nginx   default-http-backend-5bcc9fd598-t666l     1/1     Running     0          36m
ingress-nginx   nginx-ingress-controller-76prz            1/1     Running     0          36m
ingress-nginx   nginx-ingress-controller-slfnq            1/1     Running     0          36m
ingress-nginx   nginx-ingress-controller-xpw6k            1/1     Running     0          36m
kube-system     canal-2bdlm                               2/2     Running     0          36m
kube-system     canal-742t2                               2/2     Running     0          36m
kube-system     canal-c4thr                               2/2     Running     0          36m
kube-system     coredns-799dffd9c4-j22nc                  1/1     Running     2          36m
kube-system     coredns-autoscaler-84766fbb4-vjvg9        1/1     Running     0          36m
kube-system     metrics-server-59c6fd6767-7tpll           1/1     Running     2          36m
kube-system     rke-coredns-addon-deploy-job-j7hs2        0/1     Completed   0          36m
kube-system     rke-ingress-controller-deploy-job-8wxsj   0/1     Completed   0          36m
kube-system     rke-metrics-addon-deploy-job-qp94f        0/1     Completed   0          36m
kube-system     rke-network-plugin-deploy-job-kt6w5       0/1     Completed   0          36m
```
## 2.4 保存好如下配置文件，集群的操作全靠如下俩个配置文件，若丢失集群也就丢失了
```shell
rancher-cluster.yaml
kube_config_rancher-cluster.yaml
```


## 2.4 升级
```shell

```

## 2.6 备份和恢复
```shell

```

