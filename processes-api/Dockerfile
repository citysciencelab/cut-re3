FROM geopython/pygeoapi:0.13.0

RUN python3 -m pip install --upgrade build

COPY ./config.yml /pygeoapi/local.config.yml
COPY ./model1/ /pygeoapi/pygeoapi/process/
COPY ./requirements.txt ./

RUN pip install -r requirements.txt
