# 1 服务端安装
## 1.1 服务端安装
```Shell
sudo apt-get install -y nfs-kernel-server
```

## 1.2 创建目录，并解除目录权限
```shell
mkdir -p /nfs && chown nobody:nogroup /nfs
```
## 1.3 更改配置文件
```
ro：目录是只读共享的,客户端计算机将无法写入它。这是默认值。
rw：客户端计算机将具有对目录的读写权限。
no_root_squash：默认情况下，用户root在客户端计算机上发出的任何文件请求都被视为由服务器上的用户nobody创建。（确切地说，请求映射到的UID取决于服务器上用户“nobody”的UID，而不是客户端。）如果 选择了 no_root_squash，则客户端计算机上的root将具有相同级别的访问权限。系统作为服务器上的root用户。这可能会产生严重的安全隐患，但如果您要在涉及导出目录的客户端计算机上执行任何管理工作，则可能需要这样做。如果没有充分的理由，您不应该指定此选项。
no_subtree_check：如果只导出部分卷，则称为子树检查的例程将验证从客户端请求的文件是否在卷的相应部分中。如果导出整个卷，则禁用此检查将加快传输速度。
sync：默认情况下，除了最新版本（版本1.11）之外的所有 exportfs 命令都将使用异步行为，告诉客户端计算机文件写入完成 - 也就是说，已经写入稳定存储 - 当NFS处理完成时写入文件系统。如果服务器重新启动，此行为可能会导致数据损坏，并且 sync 选项会阻止此操作。 

IP可以是如下方式
* .foo.com或 192.168.*.*
```
```shell
vi /etc/exports
/nfs 10.5.1.124(rw,sync,no_subtree_check) 
/nfs 10.5.1.125(rw,sync,no_subtree_check) 
/nfs 10.5.1.126(rw,sync,no_subtree_check)
```
## 1.4 重载配置
```shell
exportfs -ra
```
## 1.5 重启nfs-kernel-server,并设置开机启动
```shell
sudo systemctl restart nfs-kernel-server
sudo systemctl enable nfs-kernel-server
```

# 2 客户端安装(PaaS中的slave节点)
## 2.1 安装客户端common包
```shell
sudo apt install -y nfs-common
```

## 2.2 客户端查看,发布的共享目录
```shell
sudo showmount -e serverIP
```

## 2.2 客户端执行远程mount命令
```shell
格式：mount 服务端ip:/共享目录   /客户端需要共享的目录
示例: mount 10.5.1.111:/nfs /nfs/123
      或 mount -t nfs 10.5.1.111:/nfs /nfs/123

卸载 umount /nfs/123
```
# 3 测试
```shell
cd /nfs/123
touch 123
```
