import logging
import logging.config
import os
import sys


'''
Priority of log CONFIG file location
    1. check if environment variable PYMICRO_LOGCONFIG is set
    2. read from 'conf/logging_config.ini'
'''
log_configfile = os.environ.get("PYMICRO_LOGCONFIG") or \
                    os.path.join(sys.exec_prefix, "conf/logging_config.ini")
logging.config.fileConfig(log_configfile)


LOGLEVEL = os.environ.get('PYMICRO_LOGLEVEL', 'INFO').upper()
logging.getLogger().setLevel(LOGLEVEL)
