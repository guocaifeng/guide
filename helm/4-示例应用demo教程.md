### 1.1 编写应用的介绍信息
 打开 Chart.yaml, 填写你部署的应用的详细信息，以 mychart 为例：
```shell
$ cat kong-postgresql/Chart.yaml
apiVersion: v1
appVersion: "1.0.0"                  # dnc应用版本号
description: "空网关数据库"       # chart应用描述
name: kong-postgresql                        # chart应用名称
version: 0.0.1                     # chart的版本号
source: http://gitlab.cyai.com/dev01-ic/dnc-cloud/tree/r201905 #引用项目原代码，要注意最后源代码tag
home: http://10.6.33.49:8002/dnc   # 项目访问主页
icon: http://10.6.33.49:9090/rancher-imgs/postgres.jpg # chart的icon，用于在charts商店展示
keywords: #关键词
- kong-postgresql
maintainers: #维护者
- email: guocaifeng@cyai.com #邮箱
  name: guocaifeng #名字
  phone: 18810727006

```

#### 1.2 编写应用具体部署信息
 编辑 values.yaml，它默认会在 Kubernetes 部署一个 Nginx。下面是 mychart 应用的 values.yaml 文件的内容：
```shell
$ cat kong-postgresql/values.yaml
# Default values for dnc.
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

# 后端pod个数(副本数)
replicaCount: 1 
namespace: dnc
# image镜像相关内容
#   repository 镜像名称
#   tag        镜像版本号
#   pullPolicy 镜像下拉策略 Always(总是) IfNotPresent(本地有则不拉取) Never(只使用本地不拉取)
image:
  repository: postgres
  tag: 10.5                             
  pullPolicy: IfNotPresent

# 如果要添加镜像下拉秘钥，请严格按照如下格式添加secret名称，如果为空，填写[]
# imagePullSecrets:
#   - name: myregistrykey
# 或使用如下格式
# imagePullSecrets: []
imagePullSecrets: []

# 单独添加环境变量
# env: 
#   - name: DB_USER
#     value: admin
#   - name: DB_PASSWD
#     value: admin
# 或 如果没有变量添加，需要使用如下格式
# env: []
env: []
  # - name: DB_USER
  #   value: admin
  # - name: DB_PASSWD
  #   value: admin

# 可以使用如下方式引用环境变量,如果env中存在相同参数变量，此文件中变量会被覆盖
# envFrom:
#   configMapRef:
#     name: dnc-env
# 或下边这种方式
# envFrom: []
envFrom:
- configMapRef:
    name: kong-env

resources: {}
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, uncomment the following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  # limits:
  #   cpu: 100m
  #   memory: 128Mi
  # requests:
  #   cpu: 100m
  #   memory: 128Mi

# 容器映射路径
# volumeMounts: []
# 或者使用如下方式
# volumeMounts:
# - mountPath: /var/app_log
#   name: vol1
# - mountPath: /home/cyuser/dnc-cloud/dj_dnc/logs
#   name: vol2
volumeMounts:
- mountPath: /var/lib/postgresql/data
  name: vol1

# 宿主机映射路径
# volumes: []
# 或者使用如下方式
# volumes:
# - hostPath:
#     path: /srv/docker/log/dnc_app_log
#     type: ""
#   name: vol1
# - hostPath:
#     path: /srv/docker/log/dnc_app_log/dnc
#     type: ""
#   name: vol2
volumes:
- hostPath:
    path: /srv/docker/db/kong-db
    type: ""
  name: vol1


## String to partially override wordpress.fullname template (will maintain the release name)
nameOverride: ""

## String to fully override dnc.fullname template
fullnameOverride: ""

containers:
  containerPort: 5432

# service 相关内容 
# service:
#   type: NodePort  服务暴露类型，目前都是nodeport
#   port: 8000   容器端口
#   targetPort: 8000  默认与容器端口一致
#   nodePort: 8090 对外访问端口
service:
  typelower: nodeport
  type: NodePort
  port: 5432
  targetPort: 5432
  nodePort: 15434
  

# 是否启用ingress 如果是false 不启用
ingress:
  enabled: false # 不开启
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
  hosts:
    - host: chart-example.local
      paths: []

  tls: []
  #  - secretName: chart-example-tls
  #    hosts:
  #      - chart-example.local

# nodeSelector: {}
# 或者使用如下方式
# nodeSelector: 
#   dnc: dnc
nodeSelector:
  kong: kong-db

tolerations: []

affinity: {}

```

```shell
$ cat kong-postgresql/_helpers.tpl.yaml
{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "kong-postgresql.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "kong-postgresql.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kong-postgresql.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "kong-postgresql.labels" -}}
app.kubernetes.io/name: {{ include "kong-postgresql.name" . }}
helm.sh/chart: {{ include "kong-postgresql.chart" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
```

```shell
$ cat kong-postgresql/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "kong-postgresql.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
{{ include "kong-postgresql.labels" . | indent 4 }}
spec:
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ include "kong-postgresql.name" . }}
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ include "kong-postgresql.name" . }}
        app.kubernetes.io/instance: {{ .Release.Name }}
    spec:
    {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
    {{- end }}
      containers:
        - name: {{ include "kong-postgresql.name" . }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: {{ include "kong-postgresql.name" . }}
              containerPort: {{ .Values.containers.containerPort }}
              protocol: TCP
          {{- if .Values.env }}
          env: {{ toYaml .Values.env | nindent 12 }}
          {{- end }}
          {{- if .Values.envFrom }}
          envFrom: {{ toYaml .Values.envFrom | nindent 12 }}
          {{- end }}
          {{- if .Values.volumeMounts }}
          volumeMounts:
          {{- range .Values.volumeMounts }}
            - name: {{ .name }}
              mountPath: {{ .mountPath }}
          {{- end }}
          {{- end }}
          {{- if .Values.resources }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- end }}
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      {{- if .Values.volumeMounts }}
      volumes:
        {{- range .Values.volumes }}
        - name: {{ .name }}
          hostPath: 
            path: {{ .hostPath.path }}
      {{- end }}
      {{- end }} 
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}

```
```shell
$ cat kong-postgresql/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kong-env
  namespace: dnc
data:
  POSTGRES_USER: kong  #数据库使用
  POSTGRES_DB: kong    #数据库使用
  KONG_PG_HOST: 10.6.32.13  #kong-base使用
  KONG_PG_PORT: "15434"     #kong-base使用
  KONG_PG_USER: kong        #kong-base使用
  KONG_PG_DATABASE: kong        #kong-base使用
  KONG_DATABASE: postgres   #kong-base使用
  GW_ADDR: 10.6.32.13
  GW_ADMIN_PORT: "8001"
  GW_PORT: "8002"
  GW_SCHEME: http
  HOST_IP: 10.6.32.13
  KONG_ADMIN_LISTEN: 0.0.0.0:8001
  SSO_PORT: "8333" 

```
```shell
$ cat kong-postgresql/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "kong-postgresql.fullname" . }}-svc-{{ .Values.service.typelower }} 
  namespace: {{ .Values.namespace }}
  labels:
    cattle.io/creator: norman
  annotations:
    # 如果使用rancher，以下三行必须添加，会导出一些相关数据,如果使用原生集群，建议去掉以下三行数据
    field.cattle.io/targetWorkloadIds: '["deployment:{{ .Values.namespace }}:{{ include "kong-postgresql.fullname" . }}"]'
    workload.cattle.io/targetWorkloadIdNoop: "true"
    workload.cattle.io/workloadPortBased: "true"
{{ include "kong-postgresql.labels" . | indent 4 }}
spec:
  externalTrafficPolicy: Cluster
  type: {{ .Values.service.type }}
  ports:
    - name: {{ include "kong-postgresql.fullname" . }}-svc-{{ .Values.service.typelower }} 
      port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
      nodePort: {{ .Values.service.nodePort }}
  selector:
    app.kubernetes.io/name: {{ include "kong-postgresql.name" . }}  # 要跟deployment中label信息一致
    app.kubernetes.io/instance: {{ .Release.Name }}  # 要跟deployment中label信息一致
  sessionAffinity: None

```
```shell
$ cat kong-postgresql/NOTES.txt
1.如果使用rancher，需要在service中添加如下内容，位置 .metadata.labels   其他可以不按照此数据来操作
    
    field.cattle.io/targetWorkloadIds: '["deployment:{{ .Values.namespace }}:{{ include "kong-postgresql.fullname" . }}"]'
    workload.cattle.io/targetWorkloadIdNoop: "true"
    workload.cattle.io/workloadPortBased: "true"

2. 访问url地址:
    
    export HELM_NODE_PORT=$(kubectl get -n {{ .Values.namespace }} -o jsonpath="{.spec.ports[0].nodePort}" svc {{ include "kong-postgresql.fullname" . }}-svc-{{ .Values.service.typelower }})
    
    export HELM_NODE_IP=$(kubectl get nodes -n {{ .Values.namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
    
    echo http://$HELM_NODE_IP:$HELM_NODE_PORT

```

#### 1.3 检查依赖和模板配置是否正确
```shell
$ helm lint kong-postgresql
==> Linting kong-postgresql
Lint OK

1 chart(s) linted, no failures
```
 如果文件格式错误，可以根据提示进行修改。

#### 1.4 将应用打包
```shell
$ helm package kong-postgresql
Successfully packaged chart and saved it to: /root/charts/kong-postgresql-0.0.1.tgz
```
 mychart 目录会被打包为一个 kong-postgresql-0.0.1.tgz 格式的压缩包，该压缩包会被放到当前目录下，并同时被保存到了 Helm 的本地缺省仓库目录中。

 如果你想看到更详细的输出，可以加上 --debug 参数来查看打包的输出，输出内容应该类似如下：
```shell
$ helm package kong-postgresql --debug
Successfully packaged chart and saved it to: /root/charts/kong-postgresql-0.0.1.tgz
[debug] Successfully saved /root/charts/kong-postgresql-0.0.1.tgz to /root/.helm/repository/local
```

#### 1.5 使用helm插件
```shell
#查找helm主目录
rancher@rancher:~$ helm home
/home/rancher/.helm
#创建插件目录
mkdir -p /home/rancher/.helm/plugins
helm plugin install https://github.com/chartmuseum/helm-push
#测试
helm push --help
```

#### 1.6 将应用上传到helm仓库
```shell
$ helm push kong-postgresql chartmuseum
Pushing kong-postgresql-0.0.1.tgz to chartmuseum...
Done.
```

#### 1.7 查看应用
 虽然我们已经打包了 Chart 并发布到了 Helm 的本地目录中，但通过 helm search 命令查找，并不能找不到刚才生成的 mychart包。
```shell
$ helm search chartmuseum
NAME                       	CHART VERSION	APP VERSION	DESCRIPTION                        
chartmuseum/dnc            	0.0.1        	1.0.0      	供应链环境项目                     
chartmuseum/dnc-postgresql 	0.0.1        	1.0.0      	dnc数据库                          
chartmuseum/kong-gateway   	0.0.1        	1.0.0      	空网关gateway项目                  
chartmuseum/kong-postgresql	0.0.1        	1.0.0      	空网关数据库                       
chartmuseum/sso            	0.0.1        	1.0.0      	SSO项目                            
chartmuseum/sso-postgresql 	0.0.1        	1.0.0      	SSO数据库 
```

