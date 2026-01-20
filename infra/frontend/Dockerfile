FROM nginx:alpine

# nginx 프록시 설정 적용
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 프론트 정적 파일 복사
COPY . /usr/share/nginx/html/

EXPOSE 80

