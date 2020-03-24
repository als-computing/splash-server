FROM python:3.7 
#parent image directs nginx to read from /app/static, so copy
#javascript app files from build-stage into there
#COPY --from=build-stage /app/ui/dist /usr/share/nginx/html


COPY ./requirements.txt /tmp/

RUN pip install uwsgi

RUN pip install -U pip &&        pip install -r /tmp/requirements.txt
RUN useradd -ms /bin/bash uwsgi
#COPY ./ /app

EXPOSE 8000
WORKDIR /app


ENTRYPOINT  [ "uwsgi", "--socket", "0.0.0.0:3031", "--uid", "uwsgi", "--master", "--processes", "8", \
        "--protocol", "uwsgi", "--wsgi", "server:app", "--stats", "127.0.0.1:1717", "--stats-http", "--http", "0.0.0.0:8080"]