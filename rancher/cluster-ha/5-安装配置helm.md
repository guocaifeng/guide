# 1 安装helm
## 1.1 使用二进制方式安装helm
```shell
wget https://www.rancher.cn/download/helm/helm-v2.14.3-linux-amd64.tar.gz
tar -xvf helm-v2.14.3-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm && chmod +x /usr/local/bin/helm
sudo ln -s /usr/local/bin/helm /usr/bin/helm
# 验证测试
helm --help
```
## 1.2 升级helm
```shell
下载高版本直接解压即可,重复1.1步骤
```

# 2 安装Tiller
## 2.1 配置helm客户端访问授权
```shell
kubectl -n kube-system create serviceaccount tiller
kubectl create clusterrolebinding tiller \
  --clusterrole cluster-admin \
  --serviceaccount=kube-system:tiller
```
## 2.2 安装tiller
```shell
# 下载指定镜像 
docker pull registry.cyai.com/rancher/tiller:v2.14.3
或者
docker pull registry.cn-shanghai.aliyuncs.com/rancher/tiller:v2.14.3 
# 在集群中安装tiller
helm init \
--service-account tiller --skip-refresh \
--tiller-image registry.cn-shanghai.aliyuncs.com/rancher/tiller:v2.14.3 
```

## 2.3 升级tiller
```shell
# 下载指定镜像 
docker pull registry.cn-shanghai.aliyuncs.com/rancher/tiller:v2.15.2 
# 在集群中安装tiller
kubectl --namespace=kube-system \
  set image deployments/tiller-deploy \
  tiller=registry.cn-shanghai.aliyuncs.com/rancher/tiller:v2.15.2 
```

## 2.4 卸载tiller
```shell
helm reset
或者
kubectl delete deployment tiller-deploy --namespace kube-system
```