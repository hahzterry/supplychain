FROM --platform=linux/amd64 node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM --platform=linux/amd64 nginx:1.27-alpine
COPY docker/frontend/nginx.conf /etc/nginx/nginx.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

ENV COPILOTKIT_HOST=rashid-copilotkit
ENV COPILOTKIT_PORT=4000
ENV BACKEND_HOST=rashid-backend
ENV BACKEND_PORT=8000

EXPOSE 80

CMD ["/bin/sh", "-c", "export DNS_RESOLVER=$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf) && envsubst '${COPILOTKIT_HOST} ${COPILOTKIT_PORT} ${BACKEND_HOST} ${BACKEND_PORT} ${DNS_RESOLVER}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]
