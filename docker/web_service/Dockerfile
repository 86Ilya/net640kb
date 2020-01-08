from python:3.7

WORKDIR /app
COPY . /app

RUN apt-get update
RUN apt-get install -y python3-dev git vim mc
RUN pip install -r requirements.txt RUN pip install channels==2.2.0
RUN pip install channels-redis==2.4.0
