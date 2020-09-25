# 1 使用Helm安装Rancher
## 1.1 添加chart仓库
```shell
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
```

## 1.2 下载chart
```shell
helm fetch rancher-stable/rancher --version stable
```

## 1.2 使用证书安装rancher server

### 1.2.1 使用权威机构
将服务证书和CA中间证书链合并到tls.crt,将私钥复制到或者重命名为tls.key;
使用kubectl创建tls类型的secrets;
注意:
证书、私钥名称必须是tls.crt、tls.key.

```shell
# 创建命名空间
kubectl create namespace cattle-system
kubectl --kubeconfig=.kube/config \
    -n cattle-system create \
    secret tls tls-rancher-ingress \
    --cert=./tls.crt \
    --key=./tls.key

安装Rancher Server (调整自己的域名)
helm --kubeconfig=.kube/config install \
    rancher-stable/rancher \
    --name rancher \
    --namespace cattle-system \
    --set hostname=<您自己的域名> \
    --set ingress.tls.source=secret
注意:
1.创建证书对应的域名需要与hostname选项匹配，否则ingress将无法代理访问Rancher
```

### 1.2.2 使用自签名证书
之前已经生成了对应的证书，请查看 2-生成自签名证书
##### (1) 创建命名空间
```shell
kubectl --kubeconfig=.kube/config create namespace cattle-system
```
##### (2) ca证书密文
```shell
kubectl -n cattle-system create secret tls tls-rancher-ingress \
    --cert=/home/rancher/ca/tls.crt \
    --key=/home/rancher/ca/tls.key
kubectl --kubeconfig=.kube/config -n cattle-system create secret generic tls-ca --from-file=/home/rancher/ca/cacerts.pem
```
##### (3) 安装Rancher Server
```shell
helm install rancher-2.3.2.tgz --name rancher --replace \
    --namespace cattle-system \
    --set hostname=www.cyaipass.com \
    --set privateCA=true \
    --set tls=external

注意:
1.证书对应的域名需要与hostname选项匹配，否则ingress将无法代理访问Rancher。
```

## 1.3 为Cluster Pod添加主机别名(/etc/hosts)

如果您没有内部DNS服务器而是通过添加/etc/hosts主机别名的方式指定的Rancher Server域名，那么不管通过哪种方式(自定义、导入、Host驱动等)创建K8S集群，K8S集群运行起来之后，因为cattle-cluster-agent Pod和cattle-node-agent无法通过DNS记录找到Rancher Server URL,最终导致无法通信。

### 1.3.1 解决方法

可以通过给cattle-cluster-agent Pod和cattle-node-agent添加主机别名(/etc/hosts)，让其可以正常通过Rancher Server URL与Rancher Server通信(前提是IP地址可以互通)。

#### (1)执行以下命令为Rancher Server容器配置hosts:
1、替换其中的域名和IP    
2、注意json中的引号。
```shell
#指定kubectl配置文件
kubectl -n cattle-system \
    patch deployments rancher --patch '{
        "spec": {
            "template": {
                "spec": {
                    "hostAliases": [
                        {
                            "hostnames":
                            [
                                "www.cyaipass.com"
                            ],
                                "ip": "192.168.15.130"
                        }
                    ]
                }
            }
        }
    }'
```

#### (2)通过Rancher Server URL访问Rancher Web UI，设置用户名密码和Rancher Server URL地址，然后会自动登录Rancher Web UI；

https://www.cyaipass.com   会提示设置账号密码  账号默认admin  

#### (3)在Rancher Web UI中依次进入local集群/system项目，在cattle-system命名空间中查看是否有cattle-cluster-agent Pod和cattle-node-agent被创建。如果有创建则进行下面的步骤，没有创建则等待；

#### (4)编辑：cattle-cluster-agent pod
1、替换其中的域名和IP    
2、注意json中的引号。
```shell
kubectl -n cattle-system \
patch deployments cattle-cluster-agent --patch '{
    "spec": {
        "template": {
            "spec": {
                "hostAliases": [
                    {
                        "hostnames":
                        [
                            "www.cyaipass.com"
                        ],
                            "ip": "192.168.15.130"
                    }
                ]
            }
        }
    }
}'
```
#### (5)编辑：cattle-node-agent pod
1、替换其中的域名和IP    
2、注意json中的引号。
```shell
kubectl -n cattle-system \
patch daemonsets cattle-node-agent --patch '{
    "spec": {
        "template": {
            "spec": {
                "hostAliases": [
                    {
                        "hostnames":
                        [
                            "www.cyaipass.com"
                        ],
                            "ip": "192.168.15.130"
                    }
                ]
            }
        }
    }
}'

```