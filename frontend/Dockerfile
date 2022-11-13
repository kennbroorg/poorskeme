# pull the base image
FROM node:16.15.1 as development

ARG ENVIRONMENT=default

# set the working direction
WORKDIR /app

FROM development as builder

# add app
COPY . ./

# install app dependencies
COPY package.json package-lock.json ./

RUN npm i

RUN npm run build

CMD [ "npm", "start" ]