FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get upgrade -y \
  && apt-get update && apt-get install -qq -y --no-install-recommends \
  libpq-dev gdal-bin libgdal-dev \
  && apt-get clean

COPY requirements.txt ./
RUN pip install --upgrade --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
