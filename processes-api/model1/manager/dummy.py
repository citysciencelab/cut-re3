import logging

from pygeoapi.process.manager.base import BaseManager
from pygeoapi.util import JobStatus

LOGGER = logging.getLogger(__name__)


class DummyManager(BaseManager):
    """generic Manager ABC"""

    def __init__(self, manager_def):
        """
        Initialize object
        :param manager_def: manager definition
        :returns: `pygeoapi.process.manager.base.BaseManager`
        """

        super().__init__(manager_def)

    def get_jobs(self, status=None):
        """
        Get process jobs, optionally filtered by status
        :param status: job status (accepted, running, successful,
                       failed, results) (default is all)
        :returns: `list` of jobs (identifier, status, process identifier)
        """

        return []

    def execute_process(self, p, job_id, data_dict, is_async=False):
        """
        Default process execution handler
        :param p: `pygeoapi.process` object
        :param job_id: job identifier
        :param data_dict: `dict` of data parameters
        :param is_async: `bool` specifying sync or async processing.
        :returns: tuple of MIME type, response payload and status
        """

        jfmt = 'application/json'

        if is_async:
            LOGGER.debug('Dummy manager does not support asynchronous')
            LOGGER.debug('Forcing synchronous execution')

        try:
            jfmt, outputs = p.execute(data_dict)
            current_status = JobStatus.successful
        except Exception as err:
            outputs = {
                'code': 'InvalidParameterValue',
                'description': 'Error updating job'
            }
            current_status = JobStatus.failed
            LOGGER.error(err)

        return jfmt, outputs, current_status

    def __repr__(self):
        return '<Model1Manager> {}'.format(self.name)
