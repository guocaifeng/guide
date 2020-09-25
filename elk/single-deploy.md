# 1 部署单机版ELK,解析nginx-log

## 1.1 创建数据映射目录
```shell
# 创建数据存储目录
mkdir -p /root/elk-cluster/data/es01
mkdir -p /root/elk-cluster/data/es02
mkdir -p /root/elk-cluster/data/kibana
mkdir -p /root/elk-cluster/data/logstash-alarmlog
mkdir -p /root/elk-cluster/data/logstash-eventlog
mkdir -p /root/elk-cluster/data/logstash-oplog
mkdir -p /root/elk-cluster/data/logstash-syslog

# 设置目录权限
chown -R 1000:1000 /root/elk-cluster/data
chmod -R 777 /root/elk-cluster/data

# 创建配置文件目录
mkdir -p /root/elk-cluster/config/es
mkdir -p /root/elk-cluster/config/kibana
mkdir -p /root/elk-cluster/config/logstash-alarmlog
mkdir -p /root/elk-cluster/config/logstash-eventlog
mkdir -p /root/elk-cluster/config/logstash-oplog
mkdir -p /root/elk-cluster/config/logstash-syslog

# 创建备份目录
mkdir -p /mnt/es_bkup

```

## 1.2 编辑相应的配置文件

### 1.2.1 logstash.conf
```shell
$vim /root/elk-cluster/logstash/pipeline/logstash.conf
input {
    file {
        type => "nginx-access"  
        path => "/var/log/nginx/access.log"
        start_position => beginning
    }
    file {
        type => "nginx-error" 
        path => "/var/log/nginx/error.log"
        start_position => beginning
    }
}

filter {
    grok {
        match => {
             "message" => '(\[%{HTTPDATE:time_local}\]|-) (%{IPV4:remote_addr}|-) (%{USERNAME:remote_user}|-) (%{HOSTPORT:http_host}|-) (%{URIPATH:uri}|-) (%{WORD:request_method}|-) (%{NUMBER:http_status}|-) (%{INT:body_bytes_sent}|-) (%{DATA:http_referrer}|-) (%{ISO8601_SECOND:request_time}|-) (%{HOSTPORT:upstream_addr}|-) (%{NUMBER:upstream_status}|-) (%{ISO8601_SECOND:upstream_connect_time}|-) (%{ISO8601_SECOND:upstream_header_time}|-) (%{ISO8601_SECOND:upstream_response_time}|-) (%{QS:http_user_agent}) (\"%{GREEDYDATA:http_x_forwarded_for}\"|-)'
                }
        remove_tag => [ "@timestamp" ]
        remove_field => "message"
        remove_field => "_type"
        remove_field => "_id"
        }
}

output {
    elasticsearch {
        hosts => "http://es01:9200"
        manage_template => false
        index => "nginx-log-%{+YYYY.MM.dd}"
    }
}

```
### 1.2.2 logstash解析nginx日志的grok编写

```shell
(1) nginx.conf中的log_format格式如下:
'[$time_local] $remote_addr $remote_user $http_host $uri $request_method '
'$status $body_bytes_sent "$http_referer" $request_time $upstream_addr $upstream_status  '
'$upstream_connect_time $upstream_header_time $upstream_response_time '
'"$http_user_agent" "$http_x_forwarded_for" ' ;

(2) 生成日志格式:
[12/Nov/2019:10:45:43 +0800] 192.168.15.1 - 192.168.15.130:8001 /index.html GET 304 0 http://office.cyai.com:8500/mcube/ 0.000 127.0.0.1:8098 304 0.000 0.023 0.023 "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3732.400 QQBrowser/10.5.3819.400" "10.5.3.81"

(3) grok解析表达式:
(\[%{HTTPDATE:time_local}\]|-) (%{IPV4:remote_addr}|-) (%{USERNAME:remote_user}|-) (%{HOSTPORT:http_host}|-) (%{URIPATH:uri}|-) (%{WORD:request_method}|-) (%{NUMBER:http_status}|-) (%{INT:body_bytes_sent}|-) (%{DATA:http_referrer}|-) (%{ISO8601_SECOND:request_time}|-) (%{HOSTPORT:upstream_addr}|-) (%{NUMBER:upstream_status}|-) (%{ISO8601_SECOND:upstream_connect_time}|-) (%{ISO8601_SECOND:upstream_header_time}|-) (%{ISO8601_SECOND:upstream_response_time}|-) (%{QS:http_user_agent}) (\"%{GREEDYDATA:http_x_forwarded_for}\"|-)

(4) 解析后结果:
{
  "remote_addr": "192.168.15.1",
  "upstream_addr": "127.0.0.1:8098",
  "body_bytes_sent": "0",
  "upstream_header_time": "0.023",
  "time_local": "12/Nov/2019:10:45:43 +0800",
  "request_method": "GET",
  "http_host": "192.168.15.130:8001",
  "uri": "/index.html",
  "http_user_agent": "\"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3732.400 QQBrowser/10.5.3819.400\"",
  "remote_user": "-",
  "upstream_status": "304",
  "request_time": "0.000",
  "upstream_connect_time": "0.000",
  "http_x_forwarded_for": "10.5.3.81",
  "http_referrer": "http://office.cyai.com:8500/mcube/",
  "http_status": "304",
  "upstream_response_time": "0.023"
}
```

### 1.2.2 docker-compose.yml
需要修改yml文件中的地址：此地址为es访问地址：http://192.168.15.130:9200
```shell
version: '2.2'
services:
  es01:
    image: elasticsearch:7.4.2
    container_name: es01
    environment:
      - node.name=es01
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - /root/elk-cluster/data/es01:/usr/share/elasticsearch/data
    ports:
      - 9200:9200
    networks:
      - elastic

  kibana:
    image: kibana:7.4.2
    container_name: kibana
    hostname: kibana
    environment:
      SERVER_NAME: kibana
      ELASTICSEARCH_HOSTS: http://es01:9200
      XPACK_MONITORING_ENABLED: "true"
    depends_on:
      - es01
    volumes:
     - /root/elk-cluster/data/kibana:/usr/share/kibana/data
    restart: always
    ports:
      - "5601:5601"
    networks:
      - elastic

  logstash:
    image: logstash:7.4.2
    container_name: logstash
    hostname: logstash
    environment:
      - node.name=logstash
      - http.host=0.0.0.0
      - xpack.monitoring.elasticsearch.hosts=http://es01:9200
    restart: always
    depends_on:
      - es01
    volumes:
     - /root/elk-cluster/logstash/pipeline/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
     - /root/elk-cluster/data/logstash:/usr/share/logstash/data
     - /var/log/nginx/:/var/log/nginx
    ports:
      - 9600:9600
      - 5044:5044
    networks:
      - elastic

networks:
  elastic:
    driver: bridge
```

### 1.2.3 kibana访问地址

http://192.168.15.130:5601

添加index patterns:  
找到Managentment --> kibana --> index Patterns

