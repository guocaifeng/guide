## 1. Chart说明
###### Chart是helm管理应用软件的一个包，这是为了简化应用在Rancher平台进行部署的一个工具，为了规范化管理应用模板文件，现在对Chart如何编写和发布做一个规范说明。

## 2. Chart目录结构：
###### 一个完整的charts应用由如下目录结构：

![chart目录结构](http://wiki.cyai.com/download/thumbnails/26530356/%E4%BC%81%E4%B8%9A%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_15717978528763.png?version=1&modificationDate=1571797922285&api=v2 "chart目录结构")

## 3. 业务团队仅需要修改如下三个文件即可：
### 3.1 Chart.yaml文件详解
###### 此文件主要作用是记录chart的版本号，内部宝行应用的软件版本信息，记录关于该应用的项目源码地址和访问地址，方便追溯问题来源，以及chart对应的维护者，如果出现任何问题，方便运维人员快速的找到软件维护者，及时解决或修复问题。

#### 3.1.1 部分命名规范
##### 3.2.1.1.变量起名规范：
######小写字母开头，多个单词按照驼峰式来起名，尽量避免出现非字母数字以外的其他字符
```shell
举例：
chicken: true
chickenNoodleSoup: true
```
##### 3.2.1.2版本号命名规范：
###### 版本格式：主版本号.次版本号.修订号，版本号递增规则如下：
###### - 主版本号：当你做了不兼容的 API 修改，
###### - 次版本号：当你做了向下兼容的功能性新增，
###### - 修订号：当你做了向下兼容的问题修正。

###### 先行版本号及版本编译元数据可以加到“主版本号.次版本号.修订号”的后面，作为延伸。

参考此链接：https://semver.org/lang/zh-CN/



#### 3.1.2 内容示例
```yaml
#(必填) 软件api版本号，目前统一都是 v1
apiVersion: v1
#(必填) dnc应用版本号，也就是镜像的版本号，命名规则参考 https://semver.org/lang/zh-CN/
appVersion: "1.0.0"
#(选填) chart应用描述，可填写应用介绍相关信息，方便在应用商店查看
description: "dnc数据库"
#(必填) chart应用名称，软件在应用商店显示名称，小写字母+数字，并且字母开头，可以使用下划线连接。
name: dnc-postgresql
#(必填) 这是chart自身的一个版本好，如果应用不升级，那么chart升级，责需要调整此版本号
version: 0.0.1
#(选填) 项目原代码url地址，仅仅用于追踪源代码位置，没有实际用途，尽量填写完整，要注意最后源代码tag
source: http://gitlab.cyai.com/guocaifeng/helm-charts/tree/master
#(选填) 项目访问主页url地址
home: http://10.6.33.49:8002/dnc
#(选填，建议增加) chart的icon图标，用于在charts商店展示
icon: http://gitlab.cyai.com/guocaifeng/helm-charts/blob/master/icon/dnc-db.jpg
#(选填，没有实际用途) 关键词
keywords:
- dnc-postgresql
#维护者信息
maintainers:
#(必填) 邮箱
- email: guocaifeng@cyai.com
#(必填) 名字
name: guocaifeng
#(选填) 联系方式
phone: 18810727006
```

### 3.2 values.yaml文件详解
###### 应用部署的相关配置信息，全部都是必填项(可为空)

#### 3.2.1 部分命名规范
##### 3.2.1.1 变量起名规范：
###### 使用小写字母和数字组成。多字母可以使用-连接。禁止出现大写字母和下划线
```shell
举例：
drupal
cert-manager
oauth2-proxy
```
##### 3.2.1.2 设置变量语法(层叠和平铺)：
###### 建议使用平铺式写法，如果比较复杂，可以使用层叠方式提高可读性
```shell
#层叠写法:
server:
name: nginx
port: 80

#获取值时，需要加判断
{{ if .Values.server }}
{{ default "none" .Values.server.name }}
{{ end }}
```
```shell
#平铺式写法:
serverName: nginx
serverPort: 80

#获取值时，不需要加判断
{{ default "none" .Values.serverName }}
```
##### 3.2.1.3 按照写法不同，使用命令--set时写法不同：
```shell
servers:
- name: foo
port: 80
- name: bar
port: 81

#获取值时，需要加判断
--set servers[0].port=80
```
```shell
servers:
foo:
port: 80
bar:
port: 81

#获取值时，不需要加判断
--set servers.foo.port=80
```
##### 3.2.1.4 文件命名规范：
###### 自定义文件命名只能按照如下格式：
```shell
(1)多单词使用“-”连接，禁止使用驼峰式命名
my-example-configmap.yaml
(2)最后一个档次需要时资源类型
foo-pod.yaml foo-svc.yaml
```
##### 3.2.1.5 格式化模板：
###### 定义模板文件中内容时，需要在内容俩测使用**俩个空格**：
```shell
# 正确写法
{{ .foo }}
{{ print "foo" }}
# 错误写法
{{.foo}}
{{print "foo"}}
```
##### 3.2.1.6 注释格式：
###### 定义模板文件中内容时，需要在内容俩测使用**俩个空格**：
```shell
# yaml文件注释写法
# This is a comment
type: sprocket
# template文件注释写法
{{- /*
This is a comment.
*/ -}}
type: frobnitz
```

#### 3.2.2 内容示例
```shell
# 后端pod个数(副本数)
replicaCount: 1
# 属于哪个命名空间(项目)
namespace: dnc

# -------------------镜像配置 start-------------------------
# image镜像相关内容
# repository 镜像名称
# tag 镜像版本号
# pullPolicy 镜像下拉策略 Always(总是) IfNotPresent(本地有则不拉取) Never(只使用本地不拉取)
image:
repository: registry.cyai.com/lib/postgres
tag: 9.4.5.1
pullPolicy: IfNotPresent
# 如果要添加镜像下拉秘钥，请严格按照如下格式添加secret名称，如果为空，填写[]
# imagePullSecrets:
# - name: myregistrykey # 需要在rancher界面中提前预置好
# 或使用如下格式
# imagePullSecrets: []
imagePullSecrets: []
# -------------------镜像配置 start-------------------------

# -------------------环境变量配置 start-------------------------
# 单独添加环境变量，对比文件引用，优先级相对较高，优先使用此处定义的环境变量
# env: 
# - name: DB_USER
# value: admin
# - name: DB_PASSWD
# value: admin
# 或 如果没有变量添加，需要使用如下格式
# env: []
env: []
# - name: DB_USER
# value: admin
# - name: DB_PASSWD
# value: admin

# 可以使用如下方式引用环境变量,如果env中存在相同参数变量，此文件中变量会被覆盖，优先级较env低一些
# envFrom:
# configMapRef:
# name: dnc-env
# 或下边这种方式
# envFrom: []
envFrom:
- configMapRef:
name: dnc-env
# -------------------环境变量配置 end-------------------------

# -------------------资源限制 start-------------------------
# 限制应用占用服务器资源的大小，主要针对俩个维度进行限制cpu和momory，有启动时请求最小资源和运行时占用资源上限俩个方面的限制。request无法满足，容器启动失败，limits无法满足时，容器可能会自动重启(视情况而定)。
# resources:
# limits: # 资源占用上限
# cpu: 100m #cpu使用情况 m表示千分之1 例如 100m 占用0.1核 
# memory: 128Mi #内存占用上限
# requests: # 资源启动时，请求得最小资源，不满足条件，那么容器是不会启动的。
# cpu: 100m
# memory: 128Mi
resources: {}
# -------------------资源限制 end-------------------------

# -------------------服务器主机路径映射 start-------------------------
### 容器映射路径：
# 如果容器内部映射路径为空，请按照如下格式填写
# volumeMounts: []
# 如果容器内部映射路径不为空，请按照如下格式填写，多个路径按照 “-” 作为并列参数隔开
# volumeMounts:
# - mountPath: /var/app_log
# name: vol1
# - mountPath: /home/cyuser/dnc-cloud/dj_dnc/logs
# name: vol2
volumeMounts:
- mountPath: /var/lib/postgresql/data
name: vol1

### 宿主机映射路径：
# 如果宿主机映射路径为空，请按照如下格式填写：
# volumes: []
# 如果宿主机映射路径不为空，请按照如下格式填写，多个路径按照 “-” 作为并列参数隔开，volumes中name要与volumeMounts中的name 一一对应，才能将容器和宿主机路径关联起来。
# volumes:
# - hostPath:
# path: /srv/docker/log/dnc_app_log
# type: ""
# name: vol1
# - hostPath:
# path: /srv/docker/log/dnc_app_log/dnc
# type: ""
# name: vol2
volumes:
- hostPath:
path: /srv/docker/db/dnc-db
type: ""
name: vol1
# -------------------服务器主机路径映射 end-------------------------

## 先不填写，何时开放到时候再说
nameOverride: ""
## 先不填写，何时开放到时候再说
fullnameOverride: ""

# -------------------容器映射端口配置 start-------------------------
# 容器内部提供的端口号，容器自身启动时对外暴露端口
containers:
containerPort: 5432
# service相关内容，支持集群内部访问，与外部访问，以及负载均衡访问。具体设置看应用使用情况
# service:
# type: NodePort 服务暴露类型，目前都是nodeport
# port: 8000 # service自身内部暴露的端口，默认与targetPort端口一致。
# targetPort: 8000 # 这是service要代理的endpoint的端口号
# nodePort: 8090 # 宿主机映射对外访问的端口，本质是主机的一个开放的端口
service:
typelower: nodeport
type: NodePort
port: 5432
targetPort: 5432
nodePort: 15432
# -------------------容器映射端口配置 end-------------------------

# -------------------ingress配置 start-------------------------
# ingress，目前不启动此功能，后续开放式，再详细编辑参数。
ingress:
enabled: false # 不开启
annotations: {}
# kubernetes.io/ingress.class: nginx
# kubernetes.io/tls-acme: "true"
hosts:
- host: chart-example.local
paths: []

tls: []
# - secretName: chart-example-tls
# hosts:
# - chart-example.local
# -------------------ingress配置 end-------------------------

# -------------------节点亲和配置 start-------------------------
###注意：使用此功能，必须提前给服务器打标签，否则部署失败
# 强依赖关系，应用必须部署到有如下标签的服务器，如果所有服务器都没有此标签，那么部署失败，无法进行调度。
# nodeSelector: {}
# 或者使用如下方式
# nodeSelector:
# dnc: dnc
nodeSelector:
dnc: dnc-db
#
tolerations: []
#
affinity: {}
# -------------------节点亲和配置 end-------------------------
```

### 3.3 configmap.yaml文件内容介绍(目前只作为环境变量使用，如果chart中包含此文件，那么请编辑)
###### 环境外挂配置文件或者环境变量等配置类文件
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
name: dnc-env # configmap的名字
namespace: dnc # 属于哪一个项目或者命名空间
data:
# 安装如下格式 key: value 填写环境变量参数
APP_LOG_DIR: /var/app_log/dj_dnc/
CURRENT_CLIENT: dj_dnc
DB_HOST: 10.6.32.13
```
