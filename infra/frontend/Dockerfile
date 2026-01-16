FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*

COPY index.html /usr/share/nginx/html/
COPY html/ /usr/share/nginx/html/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/
COPY img/ /usr/share/nginx/html/img/

RUN echo 'server { \
    listen 8002; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    location / { \
        try_files $uri $uri/ =404; \
    } \
    \
    location = / { \
        try_files /index.html =404; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 8002

CMD ["nginx", "-g", "daemon off;"]
