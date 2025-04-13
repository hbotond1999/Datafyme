FROM nginx:stable-alpine

COPY python-code-runner.conf /etc/nginx/conf.d/default.conf

EXPOSE 8050

CMD ["nginx", "-g", "daemon off;"]