# 官方提供 内部版本3.6.9
FROM python:3.6

LABEL maintainers=guocaifeng@cyai.com

RUN mkdir -p /home/harbor/ && pip install requests==2.22.0 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

COPY app/* /home/harbor/

WORKDIR /home/harbor/

CMD ["/bin/bash","-c","python3 harbor_clear.py"]