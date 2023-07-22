import datetime as dt
import os
import stat

SERVER_ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))


class FileConfig(object):
    FLAG = os.O_RDWR | os.O_APPEND | os.O_CREAT
    MODE = stat.S_IWUSR | stat.S_IRUSR
    ENCODING_MODE = 'utf-8-sig'
    CURRENT_DIR = os.path.abspath(os.getcwd())
    CURRENT_DATETIME = dt.datetime.now().strftime('%Y%m%d%H%M%S')
    # OUTPUT_DIR = os.path.join(CURRENT_DIR, 'output', CURRENT_DATETIME)
    # LOG_DIR = os.path.join(OUTPUT_DIR, 'log')
    # if not os.path.exists(OUTPUT_DIR):
    #     os.makedirs(OUTPUT_DIR)
    # if not os.path.exists(LOG_DIR):
    #     os.makedirs(LOG_DIR)
    CONFIG_DIR = os.path.join(SERVER_ROOT, 'commons/')

    def __init__(self):
        self._data_source_dir = os.path.join(SERVER_ROOT, 'data_source/')
        self._data_config_dir = os.path.join(SERVER_ROOT, 'data_loader/')

    def get_data_source_folder(self):
        return self._data_source_dir

    def get_data_config_folder(self):
        return self._data_config_dir
