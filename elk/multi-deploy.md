# 1 部署集群版ELK

## 1.1 创建数据映射目录
```shell
mkdir -p /root/elk-cluster/data/es01
mkdir -p /root/elk-cluster/data/es02
mkdir -p /root/elk-cluster/data/es03
mkdir -p /root/elk-cluster/data/kibana
mkdir -p /root/elk-cluster/data/logstash
chown -R 1000:1000 /root/elk-cluster/data
chmod -R 777 /root/elk-cluster/data
```

# 1.2 docker-compose.yml

```shell
version: '2.2'
services:
  es01:
    image: elasticsearch:7.4.2
    container_name: es01
    environment:
      - node.name=es01
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=es02,es03
      - cluster.initial_master_nodes=es01,es02,es03
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
  es02:
    image: elasticsearch:7.4.2
    container_name: es02
    environment:
      - node.name=es02
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=es01,es03
      - cluster.initial_master_nodes=es01,es02,es03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - /root/elk-cluster/data/es02:/usr/share/elasticsearch/data
    networks:
      - elastic
  es03:
    image: elasticsearch:7.4.2
    container_name: es03
    environment:
      - node.name=es03
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=es01,es02
      - cluster.initial_master_nodes=es01,es02,es03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - /root/elk-cluster/data/es03:/usr/share/elasticsearch/data
    networks:
      - elastic

  kibana:
    image: kibana:7.4.2
    container_name: kibana
    hostname: kibana
    environment:
      SERVER_NAME: kibana
      ELASTICSEARCH_HOSTS: http://es01:9200
      XPACK_MONITORING_ENABLED: true
    depends_on:
      - es01
      - es02
      - es03
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
      - es02
      - es03
    volumes:
     - /root/elk-cluster/data/logstash:/usr/share/logstash/data
    ports:
      - 9600:9600
      - 5044:5044
    networks:
      - elastic

networks:
  elastic:
    driver: bridge
```

