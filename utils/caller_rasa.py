from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu.config import RasaNLUConfig
from thriftpy.rpc import make_server

import sys
import socket, os
import hashlib
import json


OS_PATH = os.path.dirname(os.path.abspath(__file__))

class RasaServer(object):
    def __init__(self, model_path):
        self.start_interpreter(model_path)

    def start_interpreter(self, model_path):
        metadata = Metadata.load(model_path)
        self.interpreter = Interpreter.load(metadata, RasaNLUConfig(OS_PATH+"/config-rasa.json"))

    def interpretator(self, msg):
        return json.dumps(self.interpreter.parse(str(msg, 'utf-8')))


def start_new_bot(model_path):
    rasa_server = RasaServer(model_path) 
    with socket.socket(socket.AF_UNIX) as s:

        botname_hash = hashlib.sha256(model_path.encode()).hexdigest()
        try:
            os.remove("/tmp/bothub-%s.sock")
        except OSError:
            pass

        s.bind("/tmp/bothub-%s.sock" % botname_hash)
        s.listen(1)
        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)
            if not data: break
            conn.send(rasa_server.interpretator(data).encode())
            conn.close()