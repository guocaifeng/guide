FROM busybox:1.28

LABEL maintainer=guocaifeng@cyai.com \
      busybox=1.28 \
      curl=7.30.0

ADD curl-7.30.0.ermine.tar.bz2 /home

RUN mv /home/curl-7.30.0.ermine/curl.ermine /bin/curl \
    && rm -Rf /home/curl-7.30.0.ermine
