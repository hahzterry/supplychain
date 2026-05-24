FROM --platform=linux/amd64 node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY server/ ./server/
COPY tsconfig.json tsconfig.node.json ./

ENV AGENT_URL=http://rashid-backend:8001
ENV RUNTIME_PORT=4001
EXPOSE 4001

CMD ["npx", "tsx", "server/copilotkit-runtime.ts"]
