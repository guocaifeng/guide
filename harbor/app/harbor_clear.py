#!/usr/bin/env python3
# --coding:utf-8--

import json
import requests
from requests.auth import HTTPBasicAuth
from time import sleep, time
import traceback
import os

from constom_log import Logger

API_URL = os.getenv("API_URL")      # 仓库地址
USERNAME = os.getenv("USERNAME")    # 仓库用户
PASSWORD = os.getenv("PASSWORD")    # 仓库密码
EXCLUDE = os.getenv("EXCLUDE", [''])      # 排除项目
KEEP_NUM = os.getenv("KEEP_NUM", 50)      # 单镜像保留多少tag。默认50个
TIME = os.getenv("TIME", 604800)      # 多久清理一次，单位秒 默认7天清理一次
mainlog = Logger(path="./harbor-clear.log")


class Harbor(object):
    def __init__(self, api_url, user, num, exclude):
        """
        初始化一些基本参数
        :param auth: 登录账号免密
        :param head: 设置user-agent
        :param url: 登录地址
        :param project_exclude: 排除项目
        :param num_limit: 每一个repo下镜像个数
        :param project_state: project dict name and id
        :param repo_state: 需要处理的镜像仓库，将
        :param del_image_tags: 要删除的镜像
        """
        self.auth = user
        self.head = {
            "Content-Type": 'application/json',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"
        }
        self.url = api_url
        self.project_exclude = exclude
        self.num_limit = int(num)
        self.project_state = {}
        self.repo_state = {}
        self.del_image_tags = []

    def setting(self):
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.keep_alive = True

    def list_project(self):
        try:
            r_project = self.session.get("{}/projects".format(self.url), headers=self.head)
            r_project.raise_for_status()
            # 将得到的文本转换格式
            project_data = json.loads(r_project.text)  # 字符串转为字典
            for i in project_data:
                # 项目组名称
                project_name = i.get('name')
                # 项目组id
                project_id = i.get('project_id')
                # 项目组仓库
                project_repo = i.get('repo_count')
                # 利用一个字典将项目名称与id对应起来
                self.project_state[project_name] = project_id
                mainlog.info("\033[0;32m项目名称:{}\t\t项目编号:{}\t\t项目下仓库统计:{}\033[0m".format(project_name, project_id, project_repo))
            mainlog.info("\033[0;36mproject:项目组对应id列表:{}\033[0m".format(self.project_state))
        except:
            traceback.print_exc()
            raise

    def list_repo(self):
        try:
            for a in self.project_state.keys():
                # 排除部分项目组
                if a not in self.project_exclude:
                    id = self.project_state.get(a)
                    r_repo = self.session.get(
                        "{}/repositories?project_id={}".format(self.url, id),
                        headers=self.head)
                    repo_data = json.loads(r_repo.text)
                    for r in repo_data:
                        repo_name = r.get('name')
                        tag_count = r.get('tags_count')
                        # 利用字典收集｛仓库名称：tag数量｝
                        self.repo_state[repo_name] = tag_count
            mainlog.info("\033[0;31mrepo:排除项目组:{},需处理的仓库为:{}\033[0m".format(self.project_exclude, self.repo_state))
        except:
            traceback.print_exc()
            raise

    def list_repo_tag(self):
        try:
            # n 为repo 仓库名字
            for repo_name in self.repo_state.keys():
                # 如果该仓库下版本总数大于数量限制，继续往下走
                if self.repo_state.get(repo_name) > self.num_limit:
                    r_tag = self.session.get('{}/repositories/{}/tags'.format(self.url, repo_name))
                    tag_datas = json.loads(r_tag.text)
                    tag_dict = {}
                    image_tag_time_list = []
                    for tag_data in tag_datas:
                        # 镜像名字
                        image_name = repo_name + "##" + tag_data.get('name')
                        # 镜像创建时间
                        image_tag_time = tag_data.get('created')
                        tag_dict[image_name] = image_tag_time
                        image_tag_time_list.append(image_tag_time)
                    # 按照构建时间排序，保留self.num_limit个镜像，在这之前的全部删除
                    del_image_tag_time_list = sorted(image_tag_time_list, reverse=True)[self.num_limit:]
                    for k, v in tag_dict.items():
                        if v in del_image_tag_time_list:
                            self.del_image_tags.append(k)
            mainlog.info("\033[0;31mtag:本次需要删除镜像:{}\033[0m".format(self.del_image_tags))
        except:
            traceback.print_exc()
            raise

    def del_tag(self):
        try:
            delete_total = 0
            del_faild = []
            if len(self.del_image_tags) == 0:
                mainlog.info("\033[0;34mdel:本次无需删除tag\033[0m")
            else:
                mainlog.info("\033[0;34mdel:删除tag阶段耗时较长:请耐心等待\033[0m")
                for del_image_tag in self.del_image_tags:
                    try:
                        r_del = self.session.delete(
                            '{}/repositories/{}/tags/{}'.format(self.url, del_image_tag.split("##")[0],
                                                                del_image_tag.split("##")[1]),
                            headers=self.head,
                            auth=self.auth)
                        r_del.raise_for_status()
                        delete_total += 1
                    except:
                        del_faild.append(del_image_tag.split("##")[0] + ":" + del_image_tag.split("##")[1])
                mainlog.info("\033[0;34mdel:历史版本镜像已经全部清理！！共删除:{}个\033[0m".format(delete_total))
                if len(del_faild) > 0:
                    mainlog.error('删除失败共计：{}，删除失败的为：{}'.format(len(del_faild), del_faild))
        except:
            traceback.print_exc()
            raise

    def volume_recycle(self):
        try:
            if self.del_image_tags == 0:
                print("\033[0;35mvolume:本次无需清理存储\033[0m")
            else:
                # 定义一个立即执行垃圾清理的json
                da = {"schedule": {"cron": "Manual", "type": "Manual"}}
                print("\033[0;35mvolume:开始回收存储空间！\033[0m")
                r_volume = self.session.post('{}/system/gc/schedule'.format(self.url), json=da)
                r_volume.raise_for_status()
                print("\033[0;35mvolue:回收存储空间已完成！\033[0m")
        except:
            traceback.print_exc()
            raise


def start(api_url, login, num, exclude):
    start = time()
    try:
        # begin开始
        har = Harbor(api_url=api_url, user=login, num=num, exclude=exclude)
        # # 配置
        har.setting()
        # # 列出项目组
        har.list_project()
        # # 列出repo仓库
        har.list_repo()
        # # 列出tag版本
        har.list_repo_tag()
        # 删除不保留版本
        har.del_tag()
        # # 回收存储
        #har.volume_recycle()
        mainlog.info("所有操作运行完成！")
        end = time()
        allTime = end - start
        mainlog.info("运行结束共耗时:{:.2f}s".format(allTime))
    except:
        end = time()
        allTime = end - start
        # traceback.print_exc()
        mainlog.error('清理出错！')
        mainlog.error("运行结束共耗时:{:.2f}s".format(allTime))
        mainlog.error("-------------------end-----------------------")


if __name__ == '__main__':
    # 仓库API地址
    api_url = API_URL
    # 登录仓库账号、密码
    login = HTTPBasicAuth(USERNAME, PASSWORD)
    # 需要排除的项目组，自行根据情况更改，或为空
    exclude = EXCLUDE   # ['public', 'rabbitmq', 'ntp', 'elk', 'rancher', 'platform-service']
    # 仓库下版本过多，需保留的最近版本数量
    keep_num = KEEP_NUM
    # 启动Start the engine
    while True:
        start(api_url=api_url, login=login, num=keep_num, exclude=exclude)
        sleep(int(TIME))
