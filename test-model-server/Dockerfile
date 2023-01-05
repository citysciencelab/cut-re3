# FROM python:3.8-slim-buster
FROM osgeo/gdal

RUN apt update && apt upgrade -y
RUN apt install -qq -y --no-install-recommends python3-pip
RUN apt clean

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
