#! /usr/bin/python3
import argparse
import json
import logging
import os
import operator
import shutil
import socket
import sys
import threading

from . import commands

MAX_CONNECTIONS = 5
socket_path = '/tmp/litd'
queries = {}
np = None
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:(%(lineno)d):%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def setup():
    global np

    parser = argparse.ArgumentParser(description='Start the L.I.T. daemon')
    parser.add_argument('--config', '-c', dest='base_path', type=str, 
                                help='specify the directory containing the config directory')
    parser.add_argument('--gen-config', '-g', dest='gen_config_path', type=str, 
                                help='specify the new config directory ')
    args = parser.parse_args()

    default_base_path = os.path.dirname(os.path.abspath(__file__))
    if args.gen_config_path:
        try:
            shutil.copytree(os.path.join(default_base_path, 'config'), os.path.join(args.gen_config_path, 'config'))
            print("Created config directory: {}".format(args.gen_config_path))
            sys.exit(0)
        except Exception as e:
            print("Could not copy config directory: {}".format(e))
            sys.exit(1)

    logger.info('setting up')
    base_path = args.base_path if args.base_path and os.path.isdir(args.base_path) else default_base_path
    if args.base_path:
        # Create effects symlink to config path
        try:
            src = os.path.join(base_path, 'effects')
            dest = os.path.join(os.path.dirname(__file__), 'effects', 'user')
            if not os.path.exists(dest) and os.path.exists(src):
                os.symlink(src, dest)
                logger.info('Created user effects symlink')
        except OSError as e:
            logger.warning('Could not create user effects symlink: {}'.format(e))
    np = commands.commands(base_path=base_path)

    queries.update({
        'effects': effects(),
        'presets': presets(),
        'colors': colors(),
        'sections': sections(),
        'zones': zones(),
        'speeds': speeds(),
        'sections': sections(),
        'error': error('not a valid query')
    })

def start():
    setup()
    logger.info('Starting lit daemon')
    running = True
    serv = socket.socket(socket.AF_UNIX)
    try:
        os.remove(socket_path)
    except OSError as e:
        logger.warning('Got "{}" when trying to remove {}'.format(e, socket_path))
    try:
        # Allow created socket to have non-root read and write permissions
        os.umask(0o1)
        serv.bind(socket_path)
        serv.listen(MAX_CONNECTIONS)
        logger.info('Listening on {}'.format(socket_path))
        while running:
           conn, address = serv.accept()
           start_conn_thread(conn)
    except KeyboardInterrupt:
        print("Shutting down due to keyboard interrupt")
        sys.exit(0)
    except Exception as e:
        logger.error('litd socket error: {}'.format(e))
        
def start_conn_thread(conn):
    def listener():
        while True:
            try:
                data = conn.recv(4096)
                if not data: 
                    break
                msg = data.decode()
                logger.info('received command: {}'.format(msg))
                try:
                    resp = handle_command(msg).encode()
                except Exception as e:
                    logger.error("Unexpected error while handing command")
                    resp = error("Internal error")
                logger.debug('responding: {}'.format(resp))
                # First 32 bytes is message length
                conn.send(str(len(resp)).zfill(32).encode())
                conn.send(resp)
            except Exception as e:
                logger.error('litd connection error: {}'.format(e))

    thread = threading.Thread(target=listener)
    thread.start()

def handle_command(data):
    msg = json.loads(data)
    type_error = error('type must be specified as "command" or "query"')
    if not 'type' in msg:
        return type_error
    msg_type = msg['type']
    if msg_type == 'command':
        return command(msg)
    elif msg_type == 'query':
        return query(msg)
    elif msg_type == 'dev':
        return dev_command(msg)
    else:
        return type_error

def error(msg):
    return json.dumps({'rc': 1, 'result': 'ERROR: {}'.format(msg)})

def result(data):
    data['rc'] = 0
    return json.dumps(data)

def command(msg):
    if "effect" in msg:
        ret, rc = np.start_effect(msg['effect'], msg.get('args', {}))
    elif "preset" in msg:
        ret, rc = np.start_preset(msg['preset'])
    else:
        ret = "Message must have 'effect' or 'preset' key"
        rc = 1
    return json.dumps({'result': ret, 'rc': rc})

def dev_command(msg):
    if msg.get('command', '') == 'verbosity':
        level = msg.get('args', {}).get('level', None)
        level_val = 0
        try:
            level_val = getattr(logging, level.upper())
        except AttributeError:
            return json.dumps({'result': "args['level'] must be debug, info, warning, error, or critical", 'rc': 2})
        logging.getLogger().setLevel(level_val)
        return json.dumps({'result': 'Logging level changed to {}'.format(level), 'rc': 0})
    return json.dumps({'result': 'Unknown command', 'rc': 2})

def query(msg):
    return queries[msg.get('query', 'error')]

def effects():
    return result({'effects': sorted(np.get_effects(), key=operator.itemgetter('name'))})

def presets():
    return result({'presets': sorted( np.get_presets())})

def colors():
    return result({'colors': np.get_colors()})

def sections():
    return result({'sections': list(np.get_sections())})

def zones():
    return result({'zones': list(np.get_zones())})

def speeds():
    return result({'rc': 0, 'speeds': np.get_speeds()})

if __name__ == '__main__':
    logger.info('This module must be started by calling importing and calling start()')
