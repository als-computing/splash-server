FROM python:3.6 
#parent image directs nginx to read from /app/static, so copy
#javascript app files from build-stage into there
#COPY --from=build-stage /app/ui/dist /usr/share/nginx/html


COPY ./requirements.txt /tmp/

#TODO combine these two RUN apk commands
# RUN apk add --no-cache \
#             --allow-untrusted \
#             --repository \
#              http://dl-3.alpinelinux.org/alpine/edge/testing \
#             hdf5 \
#             hdf5-dev && \
#     apk add --no-cache build-base

# RUN apk add snappy g++ snappy-dev && \ 
#         pip install -U pip && \
#         pip install -r /tmp/requirements.txt

RUN pip install uwsgi

RUN pip install -U pip &&        pip install -r /tmp/requirements.txt
COPY ./splash /app/splash
EXPOSE 8000
WORKDIR /app

#COPY  nginx/ /etc/nginx/conf.d/

#COPY ./server /app/

