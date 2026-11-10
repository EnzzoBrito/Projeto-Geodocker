FROM nginx:alpine

LABEL maintainer="Hermes Tupinamba, Carlos Garcia, Enzo Brito"
LABEL description="GeoDocker Challenge Frontend Web (Nginx + Leaflet + Tailwind)"

# Substitui a configuração padrão do Nginx pelo nosso proxy e servidor estático
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia os arquivos do frontend estático
COPY src /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
