from datetime import datetime, timedelta
from flask import Flask, json, request
import os
import requests
import logging


app = Flask(__name__)


env = os.environ
URLS = env.get("URLS")
URLS = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2f03016b-a7c8-417e-b157-cd10f28f4b1b;https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2f03016b-a7c8-417e-b157-cd10f28f4b1b"

@app.route('/', methods=["POST", "GET"])
def send():
    data = json.loads(request.data)
    alerts = data['alerts']
    for i in alerts:
        labels = i['labels']
        print("labels"+str(labels))
        annotations = i['annotations']
        time = i['startsAt']
        print("告警名称:" + str(labels.get("alertname")))
        print("告警等级:" + str(labels.get("severity")))
        print("告警主机:" + str(labels.get("node")))
        print("告警主题:" + str(annotations.get("summary")))
        print("告警详情:" + str(annotations.get("description")))
        print("告警数值:" + str(annotations.get("value")))
        print("告警时间:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("起始时间:" + str(datetime.strptime(str(time)[0:str(time).index('.')], "%Y-%m-%dT%H:%M:%S") + timedelta(hours = 8)))

        if URLS is not None or URLS != "":
            for URL in URLS.split(";"):
                if format_data(labels, annotations, time, url=URL):
                    print("告警发送成功")
                else:
                    print("告警发送失败")
        else:
            print("url未设置,无法发送告警")
    return ""

def format_data(labels, annotations, time, url):
    target_data = None
    if str(labels.get("severity")) == "Warning":
        target_data = "{ \
\"msgtype\": \"markdown\", \
\"markdown\": {\"content\": \"\
>告警名称:<font color=\\\"comment\\\">  " + str(labels.get("alertname")) + "</font> \n \
>告警等级:<font color=\\\"comment\\\">  " + str(labels.get("severity")) + "</font> \n \
>告警主机:<font color=\\\"comment\\\">  " + str(labels.get("node")) + "</font> \n \
>告警主题:<font color=\\\"comment\\\">  " + str(annotations.get("summary")) + "</font> \n \
>告警详情:<font color=\\\"comment\\\">  " + str(annotations.get("description")) + "</font> \n \
>告警数值:<font color=\\\"comment\\\">  " + str(annotations.get("value")) + "</font> \n \
>告警时间:<font color=\\\"comment\\\">  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "</font> \n \
>起始时间:<font color=\\\"comment\\\">  " + str(datetime.strptime(str(time)[0:str(time).index('.')], "%Y-%m-%dT%H:%M:%S") + timedelta(hours = 8)) + "</font> \" \
} \
                     }"
    elif str(labels.get("severity")) == "Critical":
        target_data = "{ \
\"msgtype\": \"markdown\", \
\"markdown\": {\"content\": \"\
>告警名称:<font color=\\\"warning\\\">  " + str(labels.get("alertname")) + "</font> \n \
>告警等级:<font color=\\\"warning\\\">  " + str(labels.get("severity")) + "</font> \n \
>告警主机:<font color=\\\"warning\\\">  " + str(labels.get("node")) + "</font> \n \
>告警主题:<font color=\\\"warning\\\">  " + str(annotations.get("summary")) + "</font> \n \
>告警详情:<font color=\\\"warning\\\">  " + str(annotations.get("description")) + "</font> \n \
>告警数值:<font color=\\\"warning\\\">  " + str(annotations.get("value")) + "</font> \n \
>告警时间:<font color=\\\"warning\\\">  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "</font> \n \
>起始时间:<font color=\\\"warning\\\">  " + str(datetime.strptime(str(time)[0:str(time).index('.')], "%Y-%m-%dT%H:%M:%S") + timedelta(hours = 8)) + "</font> \" \
} \
                    }"
    else:
        target_data = "{ \
\"msgtype\": \"markdown\", \
\"markdown\": {\"content\": \"\
我是机器人Prometheus，请多关照！！！\" \
} \
                    }"
    response = requests.post(url=url, data=target_data.encode('utf-8'))
    if response.ok:
        logging.info("告警发送成功")
        return True
    else:
        logging.debug("告警推送异常,异常内容:" + str(response))
        return False


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    # 10.6.0.194:8000





# data = {'receiver': 'webhook', 'status': 'firing', 'alerts': [{'status': 'firing',
#                                                         'labels': {'Node': 'instance', 'alertname': '节点状态',
#                                                                    'instance': '10.6.2.4:9100',
#                                                                    'job': 'node-export', 'severity': 'Critical'},
#                                                         'annotations': {'description': '当前服务器可能已经宕机,请及时排查问题',
#                                                                         'summary': '服务器故障', 'value': '0'},
#                                                         'startsAt': '2019-10-25T10:53:20.873303345+08:00',
#                                                         'endsAt': '0001-01-01T00:00:00Z',
#                                                         'generatorURL': 'http://prometheus:9090/graph?g0.expr=up%7Bjob%3D%22node-export%22%7D+%3D%3D+0&g0.tab=1'}],
#  'groupLabels': {'alertname': '节点状态'},
#  'commonLabels': {'Node': 'instance', 'alertname': '节点状态', 'instance': '10.6.2.4:9100', 'job': 'node-export',
#                   'severity': 'Critical'},
#  'commonAnnotations': {'description': '当前服务器可能已经宕机,请及时排查问题', 'summary': '服务器故障', 'value': '0'},
#  'externalURL': 'http://alertmanager:9093', 'version': '4', 'groupKey': '{}:{alertname="节点状态"}'}
