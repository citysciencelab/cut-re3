FROM geopython/pygeoapi:0.13.0

RUN python3 -m pip install --upgrade build

COPY ./cut.config.yml /pygeoapi/local.config.yml

COPY ./model1/ /pygeoapi/pygeoapi/process/

RUN cd /pygeoapi/pygeoapi/process/ \
	&& python3 -m build \
	&& echo ${PYTHONPATH} \
	&& cd -




