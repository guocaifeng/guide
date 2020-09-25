# 1 准备

## 1.1下载镜像
docker pull chartmuseum/chartmuseum:v0.9.0
docker pull idobry/chartmuseumui:0.0.7

## 1.2 创建存储数据目录
mkdir /root/chartmuseum/charts
chmod -R 777 /root/chartmuseum/charts   添加权限

## 1.3 启动
docker-compose up -d


# 2 参考内容
https://github.com/chartmuseum
https://chartmuseum.com/