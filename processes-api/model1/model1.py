import logging

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError

LOGGER = logging.getLogger(__name__)

#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.2.0',
    'id': 'model1',
    'title': {
        'en': 'Hello Model1',
        'fr': 'Bonjour le Monde'
    },
    'description': {
        'en': 'An example process that takes a name as input, and echoes '
              'it back as output. Intended to demonstrate a simple '
              'process with a single literal input.',
        'fr': 'Un exemple de processus qui prend un nom en entrée et le '
              'renvoie en sortie. Destiné à démontrer un processus '
              'simple avec une seule entrée littérale.',
    },
    'keywords': ['hello world', 'example', 'echo'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://example.org/process',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'name': {
            'title': 'Name',
            'description': 'The name of the person or entity that you wish to'
                           'be echoed back as an output',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,  # TODO how to use?
            'keywords': ['full name', 'personal']
        },
        'message': {
            'title': 'Message',
            'description': 'An optional message to echo as well',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        }
    },
    'outputs': {
        'echo': {
            'title': 'Hello, world',
            'description': 'A "hello world" echo with the name and (optional)'
                           ' message submitted for processing',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'name': 'World',
            'message': 'An optional message.',
        }
    }
}


class Model1Processor(BaseProcessor):
    """Hello Model1 Processor example"""

    def __init__(self, processor_def):
        """
        Initialize object
        :param processor_def: provider definition
        :returns: pygeoapi.process.hello_world.HelloWorldProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA)

    def execute(self, data):

        mimetype = 'application/json'
        name = data.get('name', None)

        if name is None:
            raise ProcessorExecuteError('Cannot process without a name')

        value = 'Hello {}! {}'.format(name, data.get('message', '')).strip()

        outputs = {
            'id': 'echo',
            'value': value
        }

        return mimetype, outputs

    def __repr__(self):
        return '<Model1Processor> {}'.format(self.name)
