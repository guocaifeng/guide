FROM python:3.7.5
LABEL maintainer="guocaifeng@cyai.com"
COPY app.py /usr/app.py
COPY run.sh /usr/run.sh
RUN pip install flask requests && chmod +x /usr/run.sh
WORKDIR /usr
EXPOSE 5000
ENTRYPOINT ["/usr/run.sh"]
