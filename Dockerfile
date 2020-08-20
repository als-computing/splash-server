FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
#parent image directs nginx to read from /app/static, so copy
#javascript app files from build-stage into there
#COPY --from=build-stage /app/ui/dist /usr/share/nginx/html


COPY ./requirements.txt /tmp/

RUN pip install -U pip &&        pip install -r /tmp/requirements.txt
COPY ./ /app
