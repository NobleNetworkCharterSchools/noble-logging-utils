"""
papertrail_logger.py

Logging setup to push log messages to Papertrail and stdout. Adapted from
http://help.papertrailapp.com/kb/configuration/configuring-centralized-logging-from-python-apps/
"""

import logging
from logging.handlers import SysLogHandler
import os
import sys

PAPERTRAIL_LOG_FORMAT = "%(asctime)s %(hostname)s %(jobname)s: [%(levelname)s] %(message)s"
PAPERTRAIL_DATE_FORMAT = "%b %d %H:%M:%S"

SF_LOCAL_HOSTNAME = "salesforce-local"
SF_LOG_LIVE = "salesforce-live"
SF_LOG_SANDBOX = "salesforce-sandbox"


class MissingCredentials(Exception):
    """No credentials found in env or logging_secrets module"""


class PapertrailContextFilter(logging.Filter):

    def __init__(self, hostname, jobname, *args, **kwargs):
        # To conform to log coloration on PT, which splits by whitespace
        self.hostname = hostname.replace(" ", "")
        self.jobname = jobname.replace(" ", "")
        super().__init__(*args, **kwargs)

    def filter(self, record):
        record.hostname = self.hostname
        record.jobname = self.jobname
        return True


def get_logger(jobname, hostname=SF_LOCAL_HOSTNAME):
    """
    Creates a logger with the `PapertrailContextFilter`, pointed at an
    address and port of a PT log destination.

    Positional arguments:

    * jobname:             job name to display in the Papertrail log stream

    Available keyword arguments:

    * hostname: hostname to display in the Papertrail log stream. Also becomes
                a 'system' in PT within the particular destination
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG) # allow all by default
    pt_filter = PapertrailContextFilter(hostname, jobname)
    logger.addFilter(pt_filter)
    destination_address, destination_port = _get_logging_destination()
    syslog = SysLogHandler(address=(destination_address, destination_port))
    formatter = logging.Formatter(
        PAPERTRAIL_LOG_FORMAT, datefmt=PAPERTRAIL_DATE_FORMAT
    )
    syslog.setFormatter(formatter)
    logger.addHandler(syslog)
    local_handler = logging.StreamHandler(sys.stdout)
    local_handler.setLevel(logging.DEBUG)
    logger.addHandler(local_handler)

    return logger

    #syslog.close() ?


def _get_logging_destination():
    """Get PaperTrail logging host and port from environment or secrets file.

    Look for PAPERTRAIL_HOST and PAPERTRAIL_PORT in environment, and failing
    that, look for local logging_secrets module.

    :return: tuple (<destination address>, <destination port>)
    :rtype: tuple (str, int)
    """
    try:
        destination = os.environ["PAPERTRAIL_HOST"]
        port = int(os.environ["PAPERTRAIL_PORT"])
    except KeyError:
        try:
            import logging_secrets
            destination = logging_secrets.PAPERTRAIL_HOST
            port = int(logging_secrets.PAPERTRAIL_PORT)
        except (ImportError, AttributeError) as e:
            raise MissingCredentials("Logging destination not found in env or logging module") from e

    return (destination, port)


if __name__ == "__main__":
    pass
