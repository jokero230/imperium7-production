FROM node:20-alpine AS builder

WORKDIR /playground
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /playground

COPY --from=builder /playground/dist ./dist

EXPOSE 3000

CMD ["npx", "serve", "dist"]

