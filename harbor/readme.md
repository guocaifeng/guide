# 1 项目介绍
定时清理Harbor镜像仓库,保证镜像容量足够，而不至于服务器磁盘不足

# 2 参数说明

必填项
```text
API_URL     # Harbor仓库地址 示例：API_URL="http://dockerhub.cyai.com/api"
USERNAME    # 仓库用户 示例：USERNAME="admin"
PASSWORD    # 仓库密码 示例：PASSWORD="admin"
```

非必填项
```text
EXCLUDE     # 排除项需要排除哪些项目,默认没有排除项。示例：EXCLUDE=['public', 'rabbitmq', 'ntp', 'elk', 'rancher', 'platform-service']
KEEP_NUM    # 单镜像保留多少tag. 默认值：50 KEEP_NUM=50
TIME        # 多久清理一次镜像仓库，单位秒 默认7天清理一次 TIME=60*60*24*7
```

# 3 构建镜像
将Dockerfile和harbor_clear.py放到同级目录下
```text
docker build -t dockerhub.cyai.com/public/harbor-clear:1.0.0 .
```

# 4 启动清理任务
```text
docker-compose up -d    # 后台启动应用
docker-compose stop     # 仅停止容器
docker-compose down     # 停止并且删除容器
docker-compose restart  # 仅重启容器
```