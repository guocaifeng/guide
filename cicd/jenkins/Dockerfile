FROM jenkins/jenkins:2.220
LABEL maintainer=guocaifeng@cyai.com
USER root

# 安装基础软件
RUN apt-get update \
    && apt-get -y install \
        apt-transport-https \
        ca-certificates \
        curl \
        expect \
        software-properties-common \
        vim \
        g++ \
        gcc \
        make \
        yarn

# 安装node  参考地址https://github.com/nodesource/distributions
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - && apt-get install -y nodejs

# 安装angular
RUN npm install -g @angular/cli@6.2.5

# docker repos
#RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - \
#    && echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu xenial stable" >> /etc/apt/sources.list.d/additional-repositories.list \
#    && echo "deb http://ftp-stud.hs-esslingen.de/ubuntu xenial main restricted universe multiverse" >> /etc/apt/sources.list.d/official-package-repositories.list \
#    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 437D05B5 \
#    && apt-get update
# docker
#RUN apt-get -y install docker-ce=18.06.3~ce~3-0~ubuntu

# 安装docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - \
    && apt-key fingerprint 0EBFCD88 \
    && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable" \
    && apt-get update

RUN apt-get -y install docker-ce=18.06.3~ce~3-0~ubuntu

# 安装 rancher helm 二进制文件
RUN wget -P /usr/bin/ http://10.6.32.13:9202/helm && wget -P /usr/bin/ http://10.6.32.13:9202/rancher
COPY ./helm /root/.helm

RUN usermod -aG docker jenkins \
    && chmod +x /usr/bin/rancher \
    && chmod +x /usr/bin/helm \
    && chmod -R +x /root/.helm \
    && helm repo update
