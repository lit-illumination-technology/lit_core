#! /usr/bin/python3
import argparse
import itertools
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
TRANSACTION_IDS = itertools.count(0, 1)
SOCKET_PATH = "/tmp/litd"
logger = logging.getLogger(__name__)


class LitDaemon:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s:%(name)s:(%(lineno)d):%(levelname)s:%(message)s",
        )
        parser = argparse.ArgumentParser(description="Start the L.I.T. daemon")
        parser.add_argument(
            "--config",
            "-c",
            dest="base_path",
            type=str,
            help="specify the directory containing the config directory",
        )
        parser.add_argument(
            "--gen-config",
            "-g",
            dest="gen_config_path",
            type=str,
            help="specify the new config directory ",
        )
        args = parser.parse_args()

        default_base_path = os.path.dirname(os.path.abspath(__file__))
        if args.gen_config_path:
            try:
                shutil.copytree(
                    os.path.join(default_base_path, "config"),
                    os.path.join(args.gen_config_path, "config"),
                )
                print("Created config directory: {}".format(args.gen_config_path))
                sys.exit(0)
            except Exception as e:
                print("Could not copy config directory: {}".format(e))
                sys.exit(1)

        logger.info("setting up")
        base_path = (
            args.base_path
            if args.base_path and os.path.isdir(args.base_path)
            else default_base_path
        )
        if args.base_path:
            # Create effects symlink to config path
            try:
                src = os.path.join(base_path, "effects")
                dest = os.path.join(os.path.dirname(__file__), "effects", "user")
                if not os.path.exists(dest) and os.path.exists(src):
                    os.symlink(src, dest)
                    logger.info(
                        "Created user effects symlink {} -> {}".format(src, dest)
                    )
                    logger.warning(
                        "User effects will not be available until this program is restarted"
                    )
            except OSError as e:
                logger.warning("Could not create user effects symlink: {}".format(e))
        self.commands = commands.commands(base_path=base_path)
        self.queries = {
            "effects": self.effects,
            "presets": self.presets,
            "colors": self.colors,
            "sections": self.sections,
            "zones": self.zones,
            "speeds": self.speeds,
            "pixels": self.pixels,
            "state": self.state,
            "error": lambda _: self.error("not a valid query"),
        }

    def start(self):
        logger.info("Starting lit daemon")
        running = True
        serv = socket.socket(socket.AF_UNIX)
        try:
            os.remove(SOCKET_PATH)
        except OSError as e:
            logger.warning('Got "{}" when trying to remove {}'.format(e, SOCKET_PATH))
        try:
            # Allow created socket to have non-root read and write permissions
            os.umask(0o1)
            serv.bind(SOCKET_PATH)
            serv.listen(MAX_CONNECTIONS)
            logger.info("Listening on {}".format(SOCKET_PATH))
            while running:
                conn, address = serv.accept()
                self.start_conn_thread(conn)
        except KeyboardInterrupt:
            logger.warning("Shutting down due to keyboard interrupt")
            sys.exit(0)
        except Exception as e:
            logger.exception("litd socket error")
        finally:
            self.commands.stop_loop()

    def start_conn_thread(self, conn):
        def listener():
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    msg = data.decode()
                    logger.info("received command: {}".format(msg))
                    try:
                        resp = self.handle_request(msg).encode()
                    except Exception as e:
                        logger.exception("Unexpected error while handing command")
                        resp = self.error("Internal error").encode()
                    logger.debug("responding: {}".format(resp))
                    # First 32 bytes is message length
                    conn.send(str(len(resp)).zfill(32).encode())
                    conn.send(resp)
                except Exception as e:
                    logger.exception("litd connection error")

        thread = threading.Thread(target=listener)
        thread.start()

    def handle_request(self, data):
        msg = json.loads(data)
        type_error = self.error('type must be specified as "start", "stop", or "query"')
        if "start" in msg:
            return self.start_command(msg["start"])
        if "stop" in msg:
            return self.stop_command(msg["stop"])
        elif "query" in msg:
            return self.query(msg["query"])
        elif "dev" in msg:
            return self.dev_command(msg["dev"])
        else:
            return type_error

    @staticmethod
    def error(msg):
        return json.dumps({"code": 1, "message": "ERROR: {}".format(msg)})

    @staticmethod
    def result(data):
        data["code"] = 0
        return json.dumps(data)

    def stop_command(self, msg):
        if "effect_id" in msg:
            effect_id = msg["effect_id"]
            self.commands.stop_effect(effect_id)
        elif "transaction_id" in msg:
            transaction_id = msg["transaction_id"]
            for effect_id in self.commands.get_transaction(transaction_id):
                self.commands.stop_effect(effect_id)
        return json.dumps({"message": "Stopped", "code": 0})

    def start_command(self, msg):
        if "effect" in msg:
            transaction_id = next(TRANSACTION_IDS)
            effect = msg["effect"]
            response = self.commands.start_effect(
                effect["name"],
                effect.get("args", {}),
                effect.get("properties", {}),
                transaction_id,
            )
            return json.dumps(response.as_dict())
        elif "preset" in msg:
            transaction_id = next(TRANSACTION_IDS)
            preset = msg["preset"]
            response = self.commands.start_preset(
                preset["name"], preset.get("properties", {}), transaction_id
            )
            return json.dumps(response.as_dict())
        elif "history" in msg:
            direction = msg["history"]
            if direction.get("back"):
                success = self.commands.history.back()
            elif direction.get("forward"):
                success = self.commands.history.forward()
            else:
                return json.dumps(
                    {
                        "message": "History request must specify 'forward' or 'back'",
                        "code": 1,
                    }
                )
            if not success:
                return json.dumps({"message": "Nothing to do", "code": 5})
            return json.dumps(
                {
                    "message": "Went {}".format(
                        "back" if direction.get("back") else "forward"
                    ),
                    "code": 0,
                }
            )
        else:
            return json.dumps(
                {
                    "message": "Command must be one of 'effect', 'preset', or 'modify'",
                    "code": 1,
                }
            )

    def dev_command(self, msg):
        if msg["command"] == "verbosity":
            level = msg.get("args", {}).get("level", None)
            level_val = 0
            try:
                level_val = getattr(logging, level.upper())
            except AttributeError:
                return json.dumps(
                    {
                        "message": "the verbosity level must be debug, info, warning, error, or critical",
                        "code": 2,
                    }
                )
            logging.getLogger().setLevel(level_val)
            return json.dumps(
                {"message": "Logging level changed to {}".format(level), "code": 0}
            )
        return json.dumps({"message": "Unknown command", "code": 2})

    def query(self, msg):
        return self.queries[msg.get("what", "error")]()

    def effects(self):
        return self.result(
            {
                "effects": sorted(
                    self.commands.get_effects(), key=operator.itemgetter("name")
                )
            }
        )

    def presets(self):
        return self.result({"presets": sorted(self.commands.get_presets())})

    def colors(self):
        return self.result({"colors": self.commands.get_colors()})

    def sections(self):
        return self.result({"sections": list(self.commands.get_sections())})

    def zones(self):
        return self.result({"zones": list(self.commands.get_zones())})

    def speeds(self):
        return self.result({"speeds": self.commands.get_speeds()})

    def pixels(self):
        return self.result({"pixels": self.commands.get_pixels()})

    def state(self):
        return self.result({"state": self.commands.get_state()})


def start():
    litd = LitDaemon()
    litd.start()


if __name__ == "__main__":
    logger.info("This module must be started by calling importing and calling start()")
