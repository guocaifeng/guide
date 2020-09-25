`
注：文档中(和pdf)yml文件不可直接复制，只能下载后复制使用，否则会有格式错误
`
# 1 参数简要说明：
## 1.1 自定义告警级别：
```shell
WARNING(警告), CRITICAL(临界值)
```

## 1.2 部署模式
```shell
一个 Master
多个 Slave
```

## 1.3 告警推送采用企业微信(群机器人wenhook方式告警)
企业微信新建群组，添加群机器人，获取webhook地址如下：
```shell
北京
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=445cc6b7-7957-48bb-8539-a017acb1ad51
苏州
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=083d539e-3efa-4d3d-b54f-4675c0f0a01f
```

# 2 服务器安装docker
## 2.1 安装docker,docker-compose使用如下链接安装和配置
```shell
http://wiki.cyai.com/pages/viewpage.action?pageId=31852890
```
## 2.2 下载如下镜像

```shell
# master
docker pull registry.cyai.com/monitor/grafana:6.3.5     
docker pull registry.cyai.com/monitor/prometheus:v2.12.0
docker pull registry.cyai.com/monitor/alertmanager:v0.18.0
docker pull registry.cyai.com/monitor/node-exporter:v0.18.0
docker pull registry.cyai.com/monitor/cadvisor:v0.33.0
docker pull registry.cyai.com/monitor/cy-webhook:v1.0.3

# slave
docker pull registry.cyai.com/monitor/node-exporter:v0.18.0
docker pull registry.cyai.com/monitor/cadvisor:v0.33.0
```

# 3 部署（先部署slave后部署master）：
## 3.1 从节点部署：
```shell
1.直接使用此目录下文件：/deploy/docker-compose/slave
2.启动容器
docker-compose up -d
```

## 3.2 主节点部署(root)：

### 3.2.1 创建存储数据的目录：
```shell
mkdir -p /home/cyuser/monitor-data/grafana
mkdir -p /home/cyuser/monitor-data/alertmanager
mkdir -p /home/cyuser/monitor-data/prometheus
chmod +x -R /home/cyuser/monitor-data/
chown -R 472:472 /home/cyuser/monitor-data/grafana
chown -R 65534:65534 /home/cyuser/monitor-data/prometheus
chown -R 65534:65534 /home/cyuser/monitor-data/alertmanager
```

### 3.2.2 docker-compose.yml
```shell
1.需要修改如下位置，关于webhook地址     
     格式如下：
        单个 URLS=https://url1  
        多个(分号隔开) URLS=https://url1;https://url2  
   
     注意事项：(1) 变量值不能添加双引号
              (2) 变量值开头和末尾,不能是分号

2.如果要更改数据存储目录，也请修改volume中对应的内容
```

### 3.2.3 prometheus.yml
```shell
1. targets中的 ip和port：修改为被监控服务器地址(启动node-export和cadvisor的服务器)
2. alerting中targets信息: 修改为启动alertmanager容器的服务器的地址
```

### 3.2.4 alertmanager.yml
```
1. webhook_configs中的url地址： 启动webhook容器的服务器地址(当前master服务器地址)
```

### 3.2.5 启动：
```shell
docker-compose up -d 或者 docker-compose --log-level debug up -d
注： -d                表示后台启动 
    --log-level debug  日志级别debug
```

# 后续步骤参见
http://wiki.cyai.com/pages/viewpage.action?pageId=26512858  
第6步
