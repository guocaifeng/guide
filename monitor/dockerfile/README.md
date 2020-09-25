## 1 启动企业微信微信，群消息机器人，webhook告警配置说明

### 1.1 build镜像
```shell
docker build -t registry.cyai.com/monitor/cy-webhook:v1.0.2 .
```

### 1.2 docker-compose.yml配置文件内容
```shell
version: '3'
networks:
  monitor:
    driver: bridge
services:
  webhook:
    image: registry.cyai.com/monitor/cy-webhook:v1.0.2
    container_name: webhook
    hostname: webhook
    restart: always
    environment:
      - URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f3f7e7b0-1664-4a89-9be6-b0f7907cad8e
    volumes:
      - /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime
      - /etc/timezone:/etc/timezone
      - /home/cyuser/monitor/app.py:/usr/app.py
    ports:
      - "9102:5000"
    networks:
      - monitor
```
`参数说明`
```shell
/home/cyuser/monitor/app.py 应用程序代码
URL 接收告警的企业微信群组机器人 
```

### 1.3 启动
```shell
docker-compose up -d 
```



