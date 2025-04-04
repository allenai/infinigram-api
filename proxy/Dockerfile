FROM nginx:1.27.4-alpine

COPY nginx.conf /etc/nginx/nginx.conf

ARG CONF_FILE=local.conf
COPY $CONF_FILE /etc/nginx/conf.d/default.conf

