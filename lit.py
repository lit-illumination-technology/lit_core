#! /usr/bin/python3
import argparse
import json
import socket
import sys

def start(effect, args):
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect('/tmp/litd')
        command = {'type': 'command', 'effect': effect, 'args': args}
        s.sendall(json.dumps(command).encode())
        response =  s.recv(4096).decode()
        s.close()
        return json.loads(response)
    except Exception as e:
        raise conn_error(e)

def query(query):
    response = ''
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect('/tmp/litd')
        msg = {'type': 'query', 'query': query}
        s.sendall(json.dumps(msg).encode())

        expected = int(s.recv(32).decode())
        received = 0
        while received < expected:
            msg = s.recv(1024).decode()
            received += 1024
            response += msg
        s.close()
    except Exception as e:
        raise conn_error(e)

    res = json.loads(response)
    if res.get('rc', 1) != 0:
        raise response_error(res)
    return res

def conn_error(e):
    return Exception('LIT Daemon error: {}'.format(e))

def response_error(res):
    return Exception('Daemon returned a non-zero response code(rc={}). Error={}'.format(res.get('rc', None), res.get('result', 'No message')))

def get_effects():
    return query('effects')['effects']

def get_colors():
    return query('colors')['colors']

def get_speeds():
    return query('speeds')['speeds']

def get_sections():
    return query('sections')['sections']

def get_zones():
    return query('zones')['zones']

if __name__ == '__main__':
    print('This is a library that must be imported to be used')
 
