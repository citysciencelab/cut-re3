import logging

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError
import time

LOGGER = logging.getLogger(__name__)

#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.2.0',
    'id': 'model1',
    'title': {
        'en': 'Simulation Model1',
        'de': 'Simulation Energiewende und Gentrifizierung'
    },
    'description': {
        'en': 'Run a Energiewende und Gentrifizierung simulation with input parameters: '
              'x, y. '
              'It returns a job ID.',
        'de': 'Energiewende- und Gentrifizierungssimulation'
              'mit Dateiname, x, y als input.',
    },
    'keywords': ['Energiewende', 'Gentrifizierung'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://example.org/process',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'simulation_name': {
            'title': 'Simulation name',
            'description': 'Mandatory',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,  # TODO how to use?
            'keywords': ['simulation_name', 'name']
        },
        'x': {
            'title': 'x',
            'description': 'Mandatory',
            'schema': {
                'type': 'numeric'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,  # TODO how to use?
            'keywords': ['x']
        },
        'y': {
            'title': 'y',
            'description': 'Mandatory',
            'schema': {
                'type': 'numeric'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['y']
        }
    },
    'outputs': {
        'geojson': {
            'title': 'Features as geojson',
            'description': 'geojson result of the simulation',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'simulation_name': 'Umnutzung',
            'x': 51.8,
            'y': 9.4,
        }
    }
}

class Model1Processor(BaseProcessor):
    """Processor starts a simulation Energiewende und Gentrifizierung"""

    def __init__(self, processor_def):
        """
        Initialize object
        :param processor_def: provider definition
        :returns: pygeoapi.process.model1.Model1Processor
        """

        super().__init__(processor_def, PROCESS_METADATA)

    def execute(self, data):
        mimetype = 'application/json'
        simulation_name = data.get('simulation_name', None)
        x = data.get('x', None)
        y = data.get('y', None)

        if simulation_name is None:
            raise ProcessorExecuteError('Cannot process without parameter simulation_name')

        if x is None:
            raise ProcessorExecuteError('Cannot process without parameter x')

        if y is None:
            raise ProcessorExecuteError('Cannot process without parameter y')

        time.sleep(15)

        with open("pygeoapi/process/results_XS.geojson") as f:
          result = f.read()

        outputs = {
          'geojson': result
        }

        return mimetype, outputs

    def __repr__(self):
        return '<Model1Processor> {}'.format(self.name)
