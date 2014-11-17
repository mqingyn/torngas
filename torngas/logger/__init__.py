# -*- coding: utf-8  -*-
#!/usr/local/bin/python
import logging
from ..settings_manager import settings

root_logger = logging.getLogger(settings.LOGGER_CONFIG['root_logger_name'])
root_logger.setLevel(settings.LOGGER_CONFIG['root_level'])

from client import SysLogger


