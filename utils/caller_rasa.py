from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu.config import RasaNLUConfig

import sys
import socket, os
import hashlib
import json


class RasaServer(object):
    def __init__(self, model_path, config_path):
        self.interpreter = Interpreter.load(Metadata.load(model_path), RasaNLUConfig(config_path))

    def interpretator(self, msg):
        return json.dumps(self.interpreter.parse(str(msg, 'utf-8')))


def start_new_bot(uuid, model_path, config_path):

    rasa_server = RasaServer(model_path, config_path) 
    with socket.socket(socket.AF_UNIX) as s:

        try:
            os.remove("/tmp/bothub-%s.sock" % uuid)
        except OSError:
            pass

        s.bind("/tmp/bothub-%s.sock" % uuid)
        s.listen(1)
        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)
            if data:
                conn.send(rasa_server.interpretator(data).encode())
                conn.close()
            else:
                conn.close()
                