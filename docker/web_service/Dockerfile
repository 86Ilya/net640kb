from python:3.7

WORKDIR /app
COPY . /app

RUN apt-get update
RUN apt-get install -y python3-dev git

ENV SECRET_KEY='g%!k-t#g0u1vxs!3^tsxot&pc@_mqx^w!5argczlvx*p(4e*3t'
ENV DATABASE_PASSWORD=netpassword
ENV DATABASE_USER=postgres
ENV DATABASE_NAME=postgres
ENV DATABASE_HOST=db
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
RUN pip install -r requirements.txt
RUN pip install channels==2.2.0
RUN pip install channels-redis==2.4.0

EXPOSE 8000
