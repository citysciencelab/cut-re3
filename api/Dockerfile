FROM osgeo/gdal

WORKDIR /usr/src/app

RUN apt update && apt upgrade -y
RUN apt install -qq -y --no-install-recommends \
  gcc python3-dev libpq-dev python3-pip gdal-bin libgdal-dev
RUN apt clean

RUN pip install wheel

COPY requirements.txt ./
RUN pip install --upgrade --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "main.py" ]
