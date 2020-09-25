FROM nginx:1.16.1

LABEL maintainer=guocaifeng@cyai.com \
      nginx=1.16.1 \
      curl=7.30.0

ADD curl-7.30.0.ermine.tar.bz2 /home

RUN mv /home/curl-7.30.0.ermine/curl.ermine /bin/curl \
    && rm -Rf /home/curl-7.30.0.ermine

