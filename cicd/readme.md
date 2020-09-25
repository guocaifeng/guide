# 1 介绍
## 1.1 Build Jenkins镜像
使用jenkins目录下的dockerfile文件进行构建

1. docker 版本为 18.06.3
2. 构建过程中会出现网络异常问题,属于正常现象,可以多次构建,不停地重复尝试
3. 基础镜像使用:jenkins/jenkins:2.220,此镜像缺少很多插件,建议运行后更换插件源为如下链接,进行安装：
       https://mirrors.huaweicloud.com/jenkins/updates/update-center.json  
4. build完成以后得镜像名称：dockerhub.cyai.com/public/jenkins-docker:2.220

## 1.2 Build Jenkins-home镜像
使用jenkins/data目录下的dockerfile文件进行构建

1. 说明：主要数据为jenkins的内部插件数据目录的镜像，用于将jenkins插件已经一些安装数据包信息大包围
为镜像，方便管理,此安装包太大，所以不能上传到gitlab.特放到百度云盘中做备份
链接: https://pan.baidu.com/s/1_UuX7KFDGfz-5vvqQlI5Aw 提取码: rnh4
2. 镜像名称：dockerhub.cyai.com/public/jenkins-home:2.220

3. 原理：将jenkins启动后，安装相关依赖插件后，将/var/jenkins_home目录下所有内容，整体打包到一个镜像中
```
# 映射目录结构：/root/jenkins/cicd/app/data:/var/jenkins_home
cd /root/jenkins/cicd/app && tar -cvf jenkins-home.tar  data
```

## 1.3 docker-compose参数介绍
以下参数为访问PaaS的api&key,需要从PaaS平台中获取    
PAAS_URL  
PAAS_TOKEN  
```
    environment:
      - PAAS_URL="https://paas.cyai.com/v3"
      - PAAS_TOKEN="token-9pgjk:h4927mttc295gqd2pjxlj5l9brb9z48zld8lxp6458jc5thh5wth6n"
```


# 2 部署
## 2.1 非插件部署
```
mkdir -p /root/jenkins/
cd /root/jenkins/
git clone http://guocaifeng:guocaifeng@gitlab.cyai.com/common-service/cicd.git
cd /root/jenkins/cicd/app

# 数据映射位置，如果需要更改，按照需求进行调整即可
docker-compose up -d  
```
## 2.2 插件部署

> 数据镜像中包含部分测试信息，具体信息如下：  
用户账号：guocaifeng/guocaifeng  
凭证： 包含git仓库账号密码: guocaifeng/guocaifeng  
任务列表：存在部分关于public的任务，如果不需要请于UI中删除  

```
1. 下载源码到并解压
mkdir -p /root/jenkins/
cd /root/jenkins/
git clone ssh://git@gitlab.cyai.com:10022/common-service/cicd.git
cd /root/jenkins/cicd/app

2. 将容器数据从镜像内部拷贝到本地
docker run -itd --name jenkins-home dockerhub.cyai.com/public/jenkins-home:2.220
docker cp jenkins-home:/home/* .
docker rm -f jenkins

3. 启动
cd /root/jenkins/cicd/app
docker-compose up -d

4. 访问账号密码
管理员初始化账号密码：admin/admin

5.更改访问url参数
系统管理-->系统配置-->Jenkins Location-->Jenkins URL 更改为你自己服务器的IP

```

# 3 Jenkinsfile 介绍
## 3.1.准备
所有要发布的应用,确保已经发布到应用商店

## 3.2.参数说明
```
// 填写project序号，每一个项目有固定的序号。
// 序号查询位置：http://wiki.cyai.com/pages/viewpage.action?pageId=39241194 
def project_num = "39"
// 命名规范 appname 版本号 中间使用空格隔开
def apps = ['rabbitmq 1.1.0','rabbitmq-job 1.1.0']

// git源码地址  git分支或者tag
def git_url = "http://guocaifeng:guocaifeng@gitlab.cyai.com/common-service/cicd.git"
def git_tag = "1.0.1"

// 镜像仓库名字  镜像版本号,可以同时build多个镜像。
def images = ['dockerhub.cyai.com/public/cicd:1.1.0','dockerhub.cyai.com/public/cicd:1.1.1']

// 是否更新app，YES表示更新，NO表示部署
def upgrade_app = "YES"

// 仓库地址
def registry_url = "dockerhub.cyai.com"

```
