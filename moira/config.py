import argparse
import os
import socket

import anyjson
import yaml

try:
    import ujson

    ujson.loads("{}")
    if anyjson._modules[0][0] != 'ujson':
        anyjson._modules.insert(
            0,
            ("ujson",
             "dumps",
             TypeError,
             "loads",
             ValueError,
             "load"))
    anyjson.force_implementation('ujson')
except ImportError:
    ujson = None

CONFIG_PATH = '/etc/moira/config.yml'
REDIS_HOST = "localhost"
REDIS_PORT = 6379
DBID = 0
LOG_DIRECTORY = "stdout"
LOG_LEVEL = "info"
HTTP_PORT = 8081
HTTP_ADDR = ''
GRAPHITE = []
GRAPHITE_PREFIX = 'DevOps.moira'
GRAPHITE_INTERVAL = 10
NODATA_CHECK_INTERVAL = 60
CHECK_INTERVAL = 5
CHECK_LOCK_TTL = 30
STOP_CHECKING_INTERVAL = 30
METRICS_TTL = 3600
CHECKPOINT_GAP = 120
PREFIX = "/api"
HOSTNAME = socket.gethostname().split('.')[0]
BAD_STATES_REMINDER = {'ERROR': 86400, 'NODATA': 86400}
ARGS = None
COOKIE_FILTER_STATE_NAME = 'moira_filter_ok'
COOKIE_SEARCH_STRING_NAME = 'moira_search_string'


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', help='path to configuration file (default: %s)' % (CONFIG_PATH))
    parser.add_argument('-l', help='path to log directory (default: %s)' % (LOG_DIRECTORY))
    parser.add_argument('-port', help='listening port (default: %s)' % (HTTP_PORT), type=int)
    parser.add_argument('-t', help='check single trigger by id and exit')
    parser.add_argument('-n', help='checker number', type=int)
    parser.add_argument('-v', help='verbosity log', default=False, const=True, nargs='?')
    return parser


def read():
    global REDIS_HOST
    global REDIS_PORT
    global DBID
    global LOG_DIRECTORY
    global LOG_LEVEL
    global HTTP_PORT
    global HTTP_ADDR
    global GRAPHITE_PREFIX
    global GRAPHITE_INTERVAL
    global NODATA_CHECK_INTERVAL
    global CHECK_INTERVAL
    global METRICS_TTL
    global ARGS
    global STOP_CHECKING_INTERVAL
    global CONFIG_PATH

    parser = get_parser()
    args = parser.parse_args()

    ARGS = args
    if args.c:
        CONFIG_PATH = args.c

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as yml:
            cfg = yaml.load(yml)
            REDIS_HOST = cfg['redis']['host']
            REDIS_PORT = cfg['redis']['port']
            DBID = cfg['redis'].get('dbid', 0)
            LOG_DIRECTORY = cfg['worker']['log_dir']
            LOG_LEVEL = cfg['worker'].get('log_level', 'info')
            HTTP_PORT = cfg['api']['port']
            HTTP_ADDR = cfg['api']['listen']
            if 'graphite' in cfg:
                for key in cfg['graphite']:
                    if key.startswith('uri'):
                        host, port = cfg['graphite'][key].split(':')
                        GRAPHITE.append((host, int(port)))
                GRAPHITE_PREFIX = cfg['graphite']['prefix']
                GRAPHITE_INTERVAL = cfg['graphite']['interval']
            NODATA_CHECK_INTERVAL = cfg['checker'].get('nodata_check_interval', 60)
            CHECK_INTERVAL = cfg['checker'].get('check_interval', 5)
            METRICS_TTL = cfg['checker'].get('metrics_ttl', 3600)
            STOP_CHECKING_INTERVAL = cfg['checker'].get('stop_checking_interval', 30)

    if args.l:
        LOG_DIRECTORY = args.l
    if args.v:
        LOG_LEVEL = 'debug'
    if args.port:
        HTTP_PORT = args.port
