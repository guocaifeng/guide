# 前提
所有服务器都必须安装python2.7
```shell script
sudo apt install python
复制 docker-compose helm kubectl 文件到ansible节点，与初始化文件init-server.yml在同一目录，并赋予权限chmod +x docker-compose helm kubectl
```

# 安装指定版本2.9.6
```shell script
sudo apt update
sudo apt install -y software-properties-common
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-cache madison ansible 
sudo apt install -y ansible=2.9.6-1ppa~bionic

# 去掉校验ssh指纹校验
sudo vi /etc/ansible/ansible.cfg
host_key_checking = False
```

# 添加要操作的机器的信息(需要使用root,避免权限问题)
```shell script
sudo vi /etc/ansible/hosts
[docker]
192.168.15.133 hostname=ansible1 ansible_ssh_port=22 ansible_ssh_user=root ansible_ssh_pass=qwe-123
192.168.15.135 hostname=ansible2 ansible_ssh_port=22 ansible_ssh_user=root ansible_ssh_pass=qwe-123
```

# 安装python
```
192.168.15.133和192.168.15.135服务器需要安装python包
sudo apt-get install -y python
```

# 测试连通性
```shell script
ansible all -m ping
```

# 执行脚本
```shell script
ansible-playbook init-server-tro.yml
```


# 常见错误
### 错误1：  
```
192.168.15.135 | FAILED! => {
    "msg": "Using a SSH password instead of a key is not possible because Host Key checking is enabled and sshpass does not support this.  Please add this host's fingerprint to your known_hosts file to manage this host."
}

解决方法
1.去掉校验(推荐)
sudo vi /etc/ansible/ansible.cfg
host_key_checking = False
2.手动添加指纹
ssh 192.168.15.135 知道输入yes

```
### 错误2：  
```
...should use /usr/bin/python3, but is using /usr/bin/python...

解决方法
更换python默认版本
sudo apt-get install -y python3.6
sudo mv /usr/bin/python /usr/bin/python.bak
sudo ln -s /usr/bin/python3.6 /usr/bin/python
回到2.7
sudo mv /usr/bin/python /usr/bin/python.bak
sudo ln -s /usr/bin/python2.7 /usr/bin/python
```
### 错误3：  
```
10.6.33.9 | FAILED! => {
    "msg": "to use the 'ssh' connection type with passwords, you must install the sshpass program"
}

解决方案
apt install sshpass
```
### 错误4： 
```
module_stdout": "/bin/sh: 1: /usr/bin/python: not found\r\n
解决方案
apt install -y python
```