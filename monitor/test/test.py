from datetime import datetime, timedelta
import requests

if __name__ == '__main__':
    # timessss = "2019-12-17T10:20:08.289129333Z"
    # print(str(datetime.strptime(str(timessss)[0:str(timessss).index('.')], "%Y-%m-%dT%H:%M:%S") + timedelta(hours=8)))
    #
    # response = requests.get(url="http://10.6.33.49:9093/api/v2/alerts")
    # print(response)

    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    aa = "98%"
    alertstr = str(aa[0:2])
    print(alertstr)
