#! /usr/bin/python3
import argparse
import json
import logging
import socket
import sys

logger = logging.getLogger(__name__)


def start_effect(effect_name, effect_args=None, properties=None):
    s = None
    if effect_args is None:
        effect_args = {}
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect("/tmp/litd")
        request = {
            "start": {
                "effect": {
                    "name": effect_name,
                    "args": effect_args,
                    "properties": properties,
                }
            }
        }
        s.sendall(json.dumps(request).encode())
    except Exception as e:
        s.close()
        raise conn_error(e)

    res = get_response(s)
    s.close()
    # rc 0: success, rc 2: command usage error
    if res.get("code", 1) != 0:
        logger.error(response_error(res))
    return res


def start_preset(preset, properties=None):
    s = None
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect("/tmp/litd")
        request = {"start": {"preset": {"name": preset, "properties": properties}}}
        s.sendall(json.dumps(request).encode())
    except Exception as e:
        s.close()
        raise conn_error(e)

    res = get_response(s)
    s.close()
    # rc 0: success, rc 2: command usage error
    if res.get("code", 1) != 0:
        logger.error(response_error(res))
    return res


def stop(effect_id=None, transaction_id=None):
    s = None
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect("/tmp/litd")
        if effect_id is not None:
            request = {"stop": {"effect_id": effect_id}}
        elif transaction_id is not None:
            request = {"stop": {"transaction_id": transaction_id}}
        else:
            raise ValueError("effect_id or transaction_id must not be None")

        s.sendall(json.dumps(request).encode())
    except Exception as e:
        s.close()
        raise conn_error(e)

    res = get_response(s)
    s.close()
    # rc 0: success, rc 2: command usage error
    if res.get("code", 1) != 0:
        logger.error(response_error(res))
    return res


def query(query):
    s = None
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect("/tmp/litd")
        msg = {"query": {"what": query}}
        s.sendall(json.dumps(msg).encode())
    except Exception as e:
        s.close()
        raise conn_error(e)

    res = get_response(s)
    s.close()
    if res.get("code", 1) != 0:
        logger.error(response_error(res))
    return res


def back():
    s = None
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect("/tmp/litd")
        msg = {"start": {"history": {"back": 1}}}
        s.sendall(json.dumps(msg).encode())
    except Exception as e:
        s.close()
        raise conn_error(e)

    res = get_response(s)
    s.close()
    if res.get("code", 1) != 0:
        logger.error(response_error(res))
    return res


def forward():
    s = None
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect("/tmp/litd")
        msg = {"start": {"history": {"forward": 1}}}
        s.sendall(json.dumps(msg).encode())
    except Exception as e:
        s.close()
        raise conn_error(e)

    res = get_response(s)
    s.close()
    if res.get("code", 1) != 0:
        logger.error(response_error(res))
    return res


def dev_command(command, args):
    s = None
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect("/tmp/litd")
        msg = {"dev": {"command": command, "args": args}}
        s.sendall(json.dumps(msg).encode())
    except Exception as e:
        s.close()
        raise conn_error(e)

    res = get_response(s)
    s.close()
    if res.get("code", 1) != 0:
        logger.error(response_error(res))
    return res


def get_response(s):
    response = ""
    try:
        # First 32 bytes are a string representation of the message length
        expected = int(s.recv(32).decode())
        received = 0
        while received < expected:
            msg = s.recv(1024).decode()
            received += 1024
            response += msg
    except Exception as e:
        raise conn_error(e)
    return json.loads(response)


def conn_error(e):
    return Exception("LIT Daemon error: {}".format(e))


def response_error(res):
    return Exception(
        "Daemon returned a non-zero response code={}. Error={}".format(
            res.get("code", None), res.get("message", "No message")
        )
    )


def get_effects():
    return query("effects")["effects"]


def get_presets():
    return query("presets")["presets"]


def get_colors():
    return query("colors")["colors"]


def get_speeds():
    return query("speeds")["speeds"]


def get_sections():
    return query("sections")["sections"]


def get_zones():
    return query("zones")["zones"]


def get_pixels():
    return query("pixels")["pixels"]


def get_state():
    return query("state")["state"]


if __name__ == "__main__":
    print("This is a library that must be imported to be used")
