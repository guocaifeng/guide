# 目前使用的jenkins-home数据包，将现有数据打包
tar -czf jenkins-home.tar data

# 上传到10.6.32.13的/root/downloadserver/download_file

# 构建镜像
docker build -t dockerhub.cyai.com/public/jenkins-home:2.220 .

# 上传到仓库
docker push dockerhub.cyai.com/public/jenkins-home:2.220



