FROM node:lts-alpine
RUN npm install -g http-server
WORKDIR /app
COPY package*.json ./
RUN npm install
RUN yarn global add parcel-bundler
COPY . .
RUN npm run build
EXPOSE 8080
# CMD [ "http-server", "dist" ]