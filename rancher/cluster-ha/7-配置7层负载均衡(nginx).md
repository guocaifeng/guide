# 3 配置负载均衡(nginx为例，只需要在rk4服务器配置即可)
我们将使用NGINX作为第4层负载均衡器(TCP)。NGINX会将所有连接转发到您的Rancher节点之一。

注意：在此配置中，负载平衡器位于Rancher节点的前面，负载均衡器可以是任意能够运行NGINX的主机。不要使用任意一个Rancher节点作为负载均衡器节点,会出现端口冲突。

## 3.1 安装nginx
### 3.1.1 编写docker-compose.yaml文件
```shell
cat >>docker-compose.yaml<<EOF
version: '3'

networks:
  nginx:
    driver: bridge

services:
  nginx-lb:
    image: nginx:1.16.1
    container_name: nginx-lb
    hostname: nginx-lb
    restart: always
    ports:
      - "80:80"  # 因为会导致端口冲突，所以此处修改过端口号
      - "443:443" # 因为会导致端口冲突，所以此处修改过端口号
    volumes:
      # 卷映射目录，按照实际情况做调整
      - /root/rancher-nginx/default.conf:/etc/nginx/conf.d/default.conf 
      - /root/rancher-nginx/nginx.conf:/etc/nginx/nginx.conf
      - /etc/localtime:/etc/localtime
      - /etc/timezone:/etc/timezone
    networks:
      - nginx
EOF
```
### 3.1.2 编写nginx.conf配置
```shell
cat >>nginx.conf<<EOF
user  nginx;
worker_processes auto;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;


events {
  worker_connections 8192;
  use epoll;
  multi_accept on;
}


http {
    tcp_nodelay on;
    proxy_http_version 1.1;
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"'
                      '$request_time $upstream_response_time $pipe';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}
EOF

```
### 3.1.3 编写default.conf配置
```shell
cat >> default.conf<<EOF
    upstream www.cyaipass.com {  
        least_conn;
        server 192.168.15.128:443 max_fails=3 fail_timeout=5s;
        server 192.168.15.136:443 max_fails=3 fail_timeout=5s;
        server 192.168.15.137:443 max_fails=3 fail_timeout=5s;
    }   
    server {
        listen 443;
        server_name www.cyaipass.com;
        server_tokens off;
        client_max_body_size 0;
        
        location / {
            proxy_pass https://www.cyaipass.com;
            proxy_redirect default;            
            proxy_buffering off;
            proxy_request_buffering off;
        }
    }
EOF
```
## 3.2 启动
```shell
docker-compose up -d
```
