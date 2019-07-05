import os
import configparser
import logging

class Config:
    '''
        Gets configuration entries from either a config file or environmnet variable.

        First, tries to get config entry from the environment using the following format
        key.sub_key=value

        If not found, the configured config file is asked for using the format:
        [key]
        sub_key=value

        '''

    def __init__(self, config_file_name = 'config.cfg'):
        self.config_parser = self.setup_config_parser(config_file_name)

    def get(self, key, sub_key, fallback=None):
        ''' Try and get a value first from an environment variable, second from the config file'''
        try:
            from_env = False
            value = os.environ.get(key + "." + sub_key)
            if value is not None:
                from_env = True
            else:
                value = self.config_parser.get(key, sub_key, fallback=fallback)
            msg = "config {}.{} = {} from env = {}".format(key, sub_key, value, from_env)
            logging.info(msg)
            return value
        except Exception as e:
            if fallback is not None:
                return fallback
            pass
            # app.logger.warn("Exception getting config value for: " + key + ":" + sub_key + str(e))

    def setup_config_parser(self, config_file_name):
        try:
            if config_file_name is None or len(config_file_name) == 0:
                logging.info("No config file name passed to Config")
                return
            config = configparser.ConfigParser()
            config.read_file(open(config_file_name))
            return config
        except Exception as e:
            logging.warning("Unexpected exception reading config file: " + str(e))

