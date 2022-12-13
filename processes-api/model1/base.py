import logging

LOGGER = logging.getLogger(__name__)


class BaseProcessor:
    """generic Processor ABC. Processes are inherited from this class"""

    def __init__(self, processor_def, process_metadata):
        """
        Initialize object
        :param processor_def: processor definition
        :param process_metadata: process metadata `dict`
        :returns: pygeoapi.processor.base.BaseProvider
        """
        self.name = processor_def['name']
        self.metadata = process_metadata

    def execute(self):
        """
        execute the process
        :returns: tuple of MIME type and process response
        """

        raise NotImplementedError()

    def __repr__(self):
        return '<BaseProcessor> {}'.format(self.name)


class ProcessorGenericError(Exception):
    """processor generic error"""
    pass


class ProcessorExecuteError(ProcessorGenericError):
    """query / backend error"""
    pass
