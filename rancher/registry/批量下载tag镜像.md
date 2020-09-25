# 批量并发镜像下拉脚本:

docker pull $name &中pull更改为rmi或者push即可执行相应操作

如果要使用tag，则比较麻烦，可依据此脚本进行更改

```
# !/bin/bash
images='
dockerhub.cyai.com/public/webhook-paas:1.0.1
dockerhub.cyai.com/public/postgres:9.4.5.1
dockerhub.cyai.com/elk/kibana:7.4.2
dockerhub.cyai.com/mes/cy_mes:V1.14.0
dockerhub.cyai.com/fpcmes/cy_fpcmes:fpcmes_hxiatestdemo
dockerhub.cyai.com/gateway/info_gateway:master_v5
dockerhub.cyai.com/kong/kong:base
dockerhub.cyai.com/oa/cy_oa:V1.7.1
'
starttime=`date +'%Y-%m-%d %H:%M:%S'`

for name in $images
do
    echo $name
    docker pull $name &
done
wait
echo "pull 完成"

endtime=`date +'%Y-%m-%d %H:%M:%S'`

start_seconds=$(date --date="$starttime" +%s);
end_seconds=$(date --date="$endtime" +%s);

echo "本次运行时间： "$((end_seconds-start_seconds))"s"

```

```text
#!/bin/bash
url=registry.cn-hangzhou.aliyuncs.com/loong576
version=v1.16.4
images=(`kubeadm config images list --kubernetes-version=$version|awk -F '/' '{print $2}'`)
for imagename in ${images[@]} ; do
  docker pull $url/$imagename
  docker tag $url/$imagename k8s.gcr.io/$imagename
  docker rmi -f $url/$imagename
done
```