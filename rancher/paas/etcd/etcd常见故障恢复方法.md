# 检查etcd是否在运行
```text
root@emeng-H110-4S:~/rancher# docker ps -a -f=name=etcd$
CONTAINER ID        IMAGE                                  COMMAND                  CREATED             STATUS              PORTS               NAMES
dadc71a4b41d        rancher/coreos-etcd:v3.3.15-rancher1   "/usr/local/bin/etcd…"   46 hours ago        Up About an hour                        etcd
``` 

# 查看etcd日志
```text
docker logs etcd

health check for peer xxx could not connect: dial tcp IP:2380: getsockopt: connection refused
无法与端口2380建立连接，检查etcd是否在此服务器上运行

xxx is starting a new election at term x	
集群已经失去法定人数，正在尝试选举新的leader。大多数etcd出故障时，会出现这个问题

connection error: desc = "transport: Error while dialing dial tcp 0.0.0.0:2379: i/o timeout"; Reconnecting to {0.0.0.0:2379 0 <nil>}
防火墙问题

rafthttp: request cluster ID mismatch	
正在尝试加入已经与另一个对等方形成的集群。该节点应从集群中删除，然后重新添加

rafthttp: failed to find member	
应从群集中删除该节点，应清除/var/lib/etcd目录，并应重新添加该节点

```

# etcd警告
```
docker exec etcd etcdctl alarm list
相关错误消息为etcdserver: mvcc: database space exceeded或applying raft message exceeded backend quota。警报NOSPACE将被触发。
解决方法：

压缩键空间
rev=$(docker exec etcd etcdctl endpoint status --write-out json | egrep -o '"revision":[0-9]*' | egrep -o '[0-9]*')
docker exec etcd etcdctl compact "$rev"
对所有etcd成员进行碎片整理
docker exec etcd etcdctl defrag --endpoints=$(docker exec etcd /bin/sh -c "etcdctl member list | cut -d, -f5 | sed -e 's/ //g' | paste -sd ','")

检查端点状态
docker exec etcd etcdctl endpoint status --endpoints=$(docker exec etcd /bin/sh -c "etcdctl member list | cut -d, -f5 | sed -e 's/ //g' | paste -sd ','") --write-out table

撤防警报，确认压缩和碎片整理后DB大小减小后，需要撤消该警报，以便etcd允许再次写入。
docker exec etcd etcdctl alarm list
docker exec etcd etcdctl alarm disarm
docker exec etcd etcdctl alarm list

```

# 问题排查常用命令
```
# 检查etcd成员状况
root@emeng-H110-4S:~/rancher# docker exec etcd etcdctl member list
8e9e05c52164694d, started, etcd-emeng-h110-4s, http://localhost:2380, https://10.6.33.49:2379,https://10.6.33.49:4001

# 检查etcd领导者状态是否正常
root@emeng-H110-4S:~/rancher# docker exec etcd etcdctl endpoint status --endpoints=$(docker exec etcd /bin/sh -c "etcdctl member list | cut -d, -f5 | sed -e 's/ //g' | paste -sd ','") --write-out table
2020-02-20 07:57:22.935872 W | pkg/flags: recognized environment variable ETCDCTL_ENDPOINTS, but unused: shadowed by corresponding flag
+-------------------------+------------------+---------+---------+-----------+-----------+------------+
|        ENDPOINT         |        ID        | VERSION | DB SIZE | IS LEADER | RAFT TERM | RAFT INDEX |
+-------------------------+------------------+---------+---------+-----------+-----------+------------+
| https://10.6.33.49:2379 | 8e9e05c52164694d |  3.3.15 |   14 MB |      true |         3 |     152016 |
+-------------------------+------------------+---------+---------+-----------+-----------+------------+

# 检查etcd后端是否正常
root@emeng-H110-4S:~/rancher# docker exec etcd etcdctl endpoint health --endpoints=$(docker exec etcd /bin/sh -c "etcdctl member list | cut -d, -f5 | sed -e 's/ //g' | paste -sd ','")

2020-02-20 07:59:01.778934 W | pkg/flags: recognized environment variable ETCDCTL_ENDPOINTS, but unused: shadowed by corresponding flag
https://10.6.33.49:2379 is healthy: successfully committed proposal: took = 8.281599ms

# 检查TCP、2379的状态
for endpoint in $(docker exec etcd /bin/sh -c "etcdctl member list | cut -d, -f5"); do
   echo "Validating connection to ${endpoint}/health"
   docker run --net=host -v $(docker inspect kubelet --format '{{ range .Mounts }}{{ if eq .Destination "/etc/kubernetes" }}{{ .Source }}{{ end }}{{ end }}')/ssl:/etc/kubernetes/ssl:ro appropriate/curl -s -w "\n" --cacert $(docker exec etcd printenv ETCDCTL_CACERT) --cert $(docker exec etcd printenv ETCDCTL_CERT) --key $(docker exec etcd printenv ETCDCTL_KEY) "${endpoint}/health"
done

Validating connection to https://10.6.33.49:2379/health
{"health":"true"}

# 检查TCP / 2380的连接

for endpoint in $(docker exec etcd /bin/sh -c "etcdctl member list | cut -d, -f4"); do
  echo "Validating connection to http://10.6.33.49:2380/version";
  docker run --net=host -v $(docker inspect kubelet --format '{{ range .Mounts }}{{ if eq .Destination "/etc/kubernetes" }}{{ .Source }}{{ end }}{{ end }}')/ssl:/etc/kubernetes/ssl:ro appropriate/curl --http1.1 -s -w "\n" --cacert $(docker exec etcd printenv ETCDCTL_CACERT) --cert $(docker exec etcd printenv ETCDCTL_CERT) --key $(docker exec etcd printenv ETCDCTL_KEY) "${endpoint}/version"
done

Validating connection to https://localhost:2380/version
{"etcdserver":"3.2.18","etcdcluster":"3.2.0"}

```


