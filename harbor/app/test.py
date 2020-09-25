#!/usr/bin/python
# -*- coding: UTF-8 -*-
from time import sleep

from requests.auth import HTTPBasicAuth

from app.harbor_clear import start

if __name__ == '__main__':
    # 仓库API地址
    api_url ="http://dockerhub.cyai.com/api"
    # 登录仓库账号、密码
    login = HTTPBasicAuth("admin", "admin")
    # 需要排除的项目组，自行根据情况更改，或为空
    exclude = ['public', 'rabbitmq', 'ntp', 'elk', 'rancher', 'platform-service']
    # 仓库下版本过多，需保留的最近版本数量
    keep_num = 100
    # 启动Start the engine
    while True:
        start(api_url=api_url, login=login, num=keep_num, exclude=exclude)
        sleep(10)