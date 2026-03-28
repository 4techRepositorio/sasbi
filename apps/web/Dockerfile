FROM node:20-alpine AS build

WORKDIR /build

# npm 10+ no Alpine pode falhar `npm ci` por peers de cadeias @angular/*; lockfile local já é a fonte de verdade.
ENV NPM_CONFIG_LEGACY_PEER_DEPS=true

COPY package.json package-lock.json ./
RUN npm ci

# Requer `.dockerignore` (exclui `node_modules`) — senão o COPY apaga o árvore limpa do `npm ci`.
COPY . .
RUN npm run build -- --configuration=production

FROM nginx:1.27-alpine

COPY --from=build /build/dist/fourpro-bi/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8081
