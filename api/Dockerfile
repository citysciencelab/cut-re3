FROM python:3

WORKDIR /usr/src/app

RUN apt update && apt upgrade -y
RUN apt install -qq -y --no-install-recommends \
  libpq-dev gdal-bin libgdal-dev
RUN apt clean

COPY requirements.txt ./
RUN pip install --upgrade --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
