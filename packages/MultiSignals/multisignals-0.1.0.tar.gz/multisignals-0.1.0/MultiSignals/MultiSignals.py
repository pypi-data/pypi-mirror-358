import socket
import requests
from flask import Flask, request, jsonify
import threading
import time
import os
import json
from typing import Dict, Any
from pathlib import Path


class infoDict(dict):
    def __init__(self, key: str, permanent: bool = False):
        self.permanent = permanent
        self.key = key
    def __repr__(self):
        return f"infoDict( dir(self) ≡≡ {{ permanent={self.permanent}, key={self.key} }} )"
    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, key, value):
        setattr(self, key, value)

class Signal:
    def __init__(self, data: Dict[str, Any]):
        self.operation = data["head"]["operation"]
        self.data = data
        self.returncode = data["head"]["returncode"]
        self.value = data["body"]["value"]
    def __repr__(self):
        return f"Signal( dir(self) ≈≡ {{ operation={self.operation}, value={self.value}, returncode={self.returncode} }} --> {self.data}) "
class MultiSignals:
    #url = "http://127.0.0.1:5000/vars"
    variables = {}

    rute = os.path.join(os.environ['APPDATA'], 'pySignals')
    rute_file = os.path.join(rute, "permanent.config")
    try:
        with open(rute_file, "r") as f:
            variables_perm = json.load(f)
        for k, v in variables_perm.items():
            variables[k] = [v, True]
    except Exception:
        pass
    def _verificar_servidor(self, host='127.0.0.1', puerto=5000):
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.settimeout(1)  # Timeout de 1 segundo
      try:
          sock.connect((host, puerto))
          return True  # El servidor está corriendo
      except (socket.timeout, socket.error):
          return False  # No hay servidor corriendo en ese puerto
      finally:
          sock.close()
    def __init__(self, daemon=True, url="http://127.0.0.1:5000/vars", host="127.0.0.1", port=5000):
        self.addAtribute("url", url)
        rute = os.path.join(os.environ['APPDATA'], 'pySignals')
        rute_file = os.path.join(rute, "permanent.config")
        if not os.path.exists(rute):
            os.mkdir(rute)
        if not os.path.exists(rute_file):
            Path(rute_file).touch()
        verify = self._verificar_servidor()
        
        if verify:
            response = requests.post(url, json={"init_code": "init_code"})
            if response.status_code == 200:
                pass
        else:
             def intermedie():
              app = Flask(__name__)
              import logging
              logging.getLogger('werkzeug')
              app.logger.setLevel(logging.ERROR)
              app.logger.disabled = True
              @app.route('/')
              def inicio():
                  recreate = {}
                  for k, v in MultiSignals.variables.items():
                      recreate[k] = v[0]
                  return jsonify(recreate), 200
              @app.route('/vars', methods=['POST'])
              def get_data():
                  data = request.get_json()
                  if data and 'init_code' in data.values():
                      return jsonify({"correct_init": "correct_init"}), 200
                  elif data and 'status' in data.values():
                      return jsonify(MultiSignals.variables), 200
                  elif data and 'register' in data.keys() and 'value' in data.keys() and 'permanent' in data.keys():
                         MultiSignals.variables[data['register']] = [data['value'], data['permanent']]
          
                         if data['permanent']:
                             try:
                              with open(f"{rute}\\permanent.config", "r+") as f:
                                 info = json.load(f)
                                 info[data["register"]] = data["value"]
                                 f.seek(0)
                                 f.truncate(0)
                                 json.dump(info, f, indent=4)
                             except Exception as e:
                                try:
                               
                                 info = {}
                                 info[data["register"]] = data["value"]
                                 with open(rute_file, "w") as d:
                                     json.dump(info, d, indent=4)
                                except Exception as e:
                                    pass
                         return jsonify({"correct": "correct"}), 200 
              
              app.run(host=host, port=port)
             
             thread = threading.Thread(target=intermedie)
             thread.daemon = daemon
             thread.start()
             for _ in range(50000):
              time.sleep(0.1)
              if self._verificar_servidor(host, port):
                break
    def send(self, signal_name, value, permanent=False) -> Signal:
        response = requests.post(self.url, json={"register": signal_name, "value": value, "permanent": permanent})
        return Signal({"head": {"operation": "send", "returncode": response.status_code}, "body": {"value": value}})
    def view(self) -> Signal:
        response = requests.post(self.url, json={"status": "status"})
        return Signal({"head": {"operation": "view", "returncode": response.status_code}, "body": {"value": response.json()}})
    def get_value(self, name):
        vars = self.view().__dict__["value"]
        if name in vars.keys():
            return vars[name][0]
        return None
    def get_mode(self, name):
        vars = self.view().__dict__["value"]
        if name in vars.keys():
            return vars[name][1]
        return None
    def addAtribute(self, key, value):
        super().__setattr__(key, value)
    def event(self, var, function, value=True, spere=0.1, times=1, in_init=False):
        def dispare():
            cicles = 0
            on = False
            if var in self.view().value.keys():
                    if self.get_value(var) == value:
                        if not on and in_init:
                            function()
                            cicles += 1
                            on = True
                        elif not in_init:
                            on = True
            while True:
                if var in self.view().value.keys():
                    if self.get_value(var) == value:
                        if not on:
                            function()
                            cicles += 1
                            on = True
                    else:
                        on = False
                if cicles == times:
                    break
                time.sleep(spere)
        thread = threading.Thread(target=dispare)
        thread.daemon = True
        thread.start()
    def restore_permanent_vars(self):
        with open(self.rute_file, "r") as f:
            try:
                data = json.load(f)
                for k, v in data.items():
                    self.send(k, v, True)
            except Exception:
                #no hay variables permanentes
                pass
    def __getitem__(self, item):
        return self.get_value(item)
    def __setitem__(self, key, value):
        if isinstance(key, str):
            return self.send(key, value, False)
        elif type(key) is infoDict:
            return self.send(key.key, value, key.permanent)
        return self.send(key, value, False)
    def __getattr__(self, name): 
        if name in dir(self):
            return super().__getattribute__(name)
        return self.get_value(name)
    def __setattr__(self, name, value):
        if name in dir(self):
            super().__setattr__(name, value)
        else:
            self.send(name, value, False)