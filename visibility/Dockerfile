FROM python:alpine3.14 as vkaci
RUN apk add --update --no-cache g++ gcc libxslt-dev libffi-dev make && pip3 install https://github.com/datacenter/pyaci/archive/master.zip kubernetes
WORKDIR /app
ENV PATH "$PATH:/app"
COPY visibility.py .
RUN chmod +x visibility.py

FROM python:alpine3.14 as vkaci-init
RUN pip3 install requests
WORKDIR /app
COPY init.py .
