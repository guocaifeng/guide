# 1 安装rancher
镜像版本 rancher/rancher:stable    
docker-compose.yaml文件内容如下:
```shell
version: '3'

networks:
  rancher:
    driver: bridge

services:
  rancher:
    image: rancher/rancher:stable
    container_name: rancher
    hostname: rancher
    restart: always
    environment:
      - AUDIT_LEVEL=3
    ports:
      - "80:80"  
      - "443:443" 
    volumes:
      - /root/rancher/data/var/lib/rancher/:/var/lib/rancher/ 
      - /root/rancher/data/var/log/auditlog:/var/log/auditlog
      - /root/rancher/ca/cacerts.pem:/etc/rancher/ssl/cacerts.pem
      - /etc/localtime:/etc/localtime
      - /etc/timezone:/etc/timezone
    networks:
      - rancher

注意：cacerts.pem需要使用上一步生成的自签名证书
```
# 2 安装nginx

## 2.1 docker-compose.yaml
```shell
version: '3'

networks:
  nginx:
    driver: bridge

services:
  nginx-lb:
    image: nginx:1.16.1
    container_name: nginx
    hostname: nginx
    restart: always
    ports:
      - "80:80"  # 因为会导致端口冲突，所以此处修改过端口号
      - "443:443" # 因为会导致端口冲突，所以此处修改过端口号
    volumes:
      # 卷映射目录，按照实际情况做调整
      - /root/nginx/default.conf:/etc/nginx/conf.d/default.conf 
      - /root/nginx/nginx.conf:/etc/nginx/nginx.conf
      - /root/nginx/ca/www.cyrancher.com.crt:/etc/cert/www.cyrancher.com.crt
      - /root/nginx/ca/www.cyrancher.com.key:/etc/cert/www.cyrancher.com.key
      - /etc/localtime:/etc/localtime
      - /etc/timezone:/etc/timezone
    networks:
      - nginx


```
## 2.2 nginx.conf
```shell
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

    log_format  main  '[$time_local] $remote_addr $remote_user $http_host $uri $request_method '
                      '$status $body_bytes_sent "$http_referer" $request_time $upstream_addr $upstream_status  '
                      '$upstream_connect_time $upstream_header_time $upstream_response_time '
                      '"$http_user_agent" "$http_x_forwarded_for" ' ;

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}

```
## 2.3 default.conf
```shell
	upstream www.cyrancher.com {
            server 192.168.15.128:443 max_fails=3 fail_timeout=5s;
	}

	map $http_upgrade $connection_upgrade {
	    default Upgrade;
	    ''      close;
	}

	server {
	    listen 443 ssl;
	    server_name www.cyrancher.com;
	    ssl_certificate /etc/cert/www.cyrancher.com.crt;
	    ssl_certificate_key /etc/cert/www.cyrancher.com.key;

	    location / {
	    	proxy_pass https://www.cyrancher.com;
	        proxy_set_header Host $host;
	        proxy_set_header X-Forwarded-Proto $scheme;
	        proxy_set_header X-Forwarded-Port $server_port;
	        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	        proxy_http_version 1.1;
	        proxy_set_header Upgrade $http_upgrade;
	        proxy_set_header Connection $connection_upgrade;
	        proxy_read_timeout 900s;
	        proxy_buffering off;
	    }
	}

	server {
	    listen 80;
	    server_name www.cyrancher.com;
	    rewrite ^(.*)$ https://$host$1 permanent;
            # return 301 https://www.cyrancher.com/g/clusters;
	}
    server {
         listen 80;
         server_name cyrancher.com;
         rewrite ^(.*)$ https://$host$1 permanent;
         # return 301 https://www.cyrancher.com/g/clusters;
    }

```