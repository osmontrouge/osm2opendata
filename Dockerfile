FROM nikolaik/python-nodejs:python3.7-nodejs12

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt && \
    npm install osmtogeojson
