# import datetime
import os
from configparser import ConfigParser

from utility._version import __version__
# from utility.save_info import info_defaults

PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))

global_confs = {'progname': 'Lambda DA',
                'progversion': __version__}

defaults = {'process_pv': [False, 'PV masked', False, 2, 515, False, False, 'PV masked', False, 'PV masked', False,
                           False]}
#             'iv': [-0.01, 0.7, 0.005, 142, 0.5, 5, 0.025, 5, 2.0, 1, 30.0]}

paths = {'icons': os.path.join(PROJECT_PATH, 'icons'),
         'last_import': PROJECT_PATH,
         'last_export': PROJECT_PATH,
         'film_db': PROJECT_PATH}

ports = {'arduino': 'dummy',
         'keithley': 'dummy'}


def read_config():
    if not os.path.exists(os.path.join(PROJECT_PATH, 'config.ini')):
        write_config()
    config = ConfigParser()
    config.read(os.path.join(PROJECT_PATH, 'config.ini'))

    for key in config['defaults']:
        defaults[key] = eval(config['defaults'][key])

    for key in config['paths']:
        paths[key] = str(config['paths'][key])

    for key in config['ports']:
        ports[key] = str(config['ports'][key])


def write_config(**kwargs):
    config_path = os.path.join(PROJECT_PATH, 'config.ini')

    config = ConfigParser()

    config['globals'] = {'progname': global_confs['progname'],
                         'progversion': global_confs['progversion']
                         }

    config['defaults'] = {'process_pv': defaults['process_pv']}
    #                       'iv': defaults['iv']}

    config['paths'] = {'icons': os.path.join(PROJECT_PATH, 'icons'),
                       'last_import': kwargs.get('import_path', paths['last_import']),
                       'last_export': kwargs.get('export_path', paths['last_export']),
                       'film_db': kwargs.get('film_db_path', paths['film_db'])
                       }

    config['ports'] = {'arduino': kwargs.get('arduino', ports['arduino']),
                       'keithley': kwargs.get('keithley', ports['keithley'])
                       }

    with open(config_path, 'w') as f:
        config.write(f)
