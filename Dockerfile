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
RUN /venv/bin/pip install -qU uwsgi PasteDeploy flask flask-cache gcloud redis
RUN apt-get remove -q -y gcc libc-dev linux-headers-amd64 manpages manpages-dev
RUN apt-get autoremove -y && apt-get clean autoclean

# the pth file for "google common apis" (https://github.com/googleapis/googleapis)
# somehow contains a keyerror... breaking all of python... nuking it for now
RUN $(/venv/bin/python -c 'print("hello")'); if [ $? != 0 ]; then \
sed -i "/\['google'\]/,+ s/^/#/" /venv/lib/python2.7/site-packages/googleapis_common_protos-*.pth; fi

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
