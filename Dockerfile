######################################
# focusgrouplogs frontend dockerfile #
######################################

FROM debian:latest
MAINTAINER Adam Talsma <se-adam.talsma@ccpgames.com>

RUN apt-get update -qq
RUN apt-get upgrade -y
RUN apt-get install -y python-dev gcc libc-dev libffi-dev libssl-dev linux-headers-amd64 ca-certificates
RUN python -c 'import urllib2;print(urllib2.urlopen("https://bootstrap.pypa.io/get-pip.py").read())' | python
RUN pip install -qU virtualenv
RUN virtualenv /venv
RUN /venv/bin/pip install -qU uwsgi PasteDeploy flask flask-cache-cassandra "gcloud!=0.10.0" redis
RUN apt-get remove -q -y gcc libc-dev linux-headers-amd64 manpages manpages-dev
RUN apt-get autoremove -y && apt-get clean autoclean

ADD MANIFEST.in /app/
ADD setup.py /app/
ADD focusgrouplogs /app/focusgrouplogs
WORKDIR /app
RUN /venv/bin/python setup.py install

RUN groupadd -r uwsgi \
&& useradd -r -g uwsgi -d /venv -s /usr/sbin/nologin -c "uwsgi user" uwsgi \
&& chown -R uwsgi:uwsgi /venv /app
USER uwsgi
ADD config /config

EXPOSE 8080
WORKDIR /

CMD /venv/bin/uwsgi --ini-paste /config
