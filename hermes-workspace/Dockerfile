FROM node:20-alpine AS builder

WORKDIR /workspace
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /workspace

COPY --from=builder /workspace ./

ENV PORT=3000
EXPOSE 3000

CMD ["npm", "start"]

