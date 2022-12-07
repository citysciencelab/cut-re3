import logging

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError
from pygeoapi.process.manager.tinydb_ import TinyDBManager
from pygeoapi.util import DATETIME_FORMAT, JobStatus
from datetime import datetime

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
                'type': 'string'
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
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['y']
        }
    },
    'outputs': {
        'job_id': {
            'title': 'Job ID',
            'description': 'Job ID of the started simulation',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'simulation_name': 'Umnutzung',
            'x': '51.8',
            'y': '9.4',
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

        LOGGER.debug(f"**** self.metadata = {self.metadata}")

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


        # manager_def = {
        #     "name": "manager_def_name",
        #     "connection": "bla",
        #     "output_dir": "foo"
        # }

        manager_def = {
            "name": "TinyDB",
            "connection": "/tmp/pygeoapi-process-manager.db",
            "output_dir": "/tmp/"
        } #config['server']['manager']

        tinyDBManager = TinyDBManager(manager_def)


        #process_id = p.metadata['id']
        #current_status = JobStatus.accepted

        job_metadata = {
            'identifier': 111111,
            'job_start_datetime': datetime.utcnow().strftime(
                DATETIME_FORMAT),
            'process_id': 'model1',
            'job_end_datetime': None,
            'status': 'accepted', #JobStatus.accepted,
            'location': None,
            'mimetype': None,
            'message': 'Job accepted and ready for execution',
            'progress': 5
        }
        value = tinyDBManager.add_job(job_metadata=job_metadata)

        outputs = {
            'id': 'job_id',
            'value': value
        }

        return mimetype, outputs

    def __repr__(self):
        return '<Model1Processor> {}'.format(self.name)
