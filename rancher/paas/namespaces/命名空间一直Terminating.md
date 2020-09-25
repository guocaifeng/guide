# 1. 命名空间一直Terminating

很多时候，执行kubectl get ns发现有一些命名空间一直处于Terminating状态，即使通过执行kubectl delete --force --grace-period=0 ns xxx去强制删除也无法删除此命名空间。

```text
举例：
一个很典型的场景：有用户想重新安装Rancher或者想把K8S集群重新导入Rancher。这个时候他可能会在K8S中直接删除cattle-system命名空间，因为底层太多资源无法删除，将会导致cattle-system命名空间一直处于Terminating状态。
因为K8S所有数据均保存在ETCD中，并且cattle-system命名空间下的资源路径均带有cattle-system字段信息。可以打印出全部路径信息，然后过滤出cattle-system命名空间相关的路径，然后将其删除。

操作步骤：
```text
# 进入任意ETCD容器
docker exec -ti <etcd_container_id/name> sh;

# 先列出所有键值对路径，再过滤目标命名空间相关的路径，最后删除过滤出来的路径;
ETCDCTL_API=3  etcdctl get / --prefix --keys-only | grep -E 'cattle-system|cattle-global-data' | xargs -i etcdctl del {}
```
