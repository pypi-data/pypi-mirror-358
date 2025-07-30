""" ... """
import time
import json

import arrow
import socketserver                         # for liveness probe (MyTCPHandler(), TCPServer)
import requests   
from   requests.exceptions import HTTPError #, ConnectionError
from   requests.adapters   import HTTPAdapter, Retry
import redis

from   datasourcelib       import Database          # wrapper for postgres/cockroach/sqlite/mongodb
from   secretmanager       import SecretManager     # for reading secrets from Vault, K8s, or environment variables

class ServerPage:
    """ ... """
    def __init__(self, prod: bool, period: int, secretcfg: dict, secretdef: dict):
        self.prod = prod
        self.type = None
        self.rsess = requests.session()
        retries = Retry(total=5,
                        backoff_factor=0.5,
                        status_forcelist=[500, 502, 503, 504])
        self.rsess.mount('https://', HTTPAdapter(max_retries=retries))
        self.secrets = self.read_secrets(secretcfg, secretdef)
        self.timezone = self.secrets.get('timezone')
        self.dba = Database(self.secrets['db_type'], self.secrets['db_params'])
        if self.secrets['rhost']:
            self.r = self.connect_redis()
        self.update_period = period
        self.last_update = 0
        self.output = False

    def read_secrets(self, secretcfg: dict, secretdef: dict):
        """ Read secrets from a file, Vault, Kubernetes, or environment variables. """
        sm = SecretManager(secretcfg, log_level='INFO')
        if secretcfg.get("SOURCE") == "FILE":
            # Read secrets from a file
            secrets = sm.read_secrets(secretdef.get("file_name"), secretdef.get("file_type"))
        elif secretcfg.get("SOURCE") == "ENVIRONMENT":
            # Read secrets from environment variables
            secrets = sm.read_secrets(secretdef.get("environment_definition"), secretdef.get("env_file"), 
                                      secretdef.get("definition_type"))
        elif secretcfg.get("SOURCE") == "KUBERNETES":
            # Read secrets from Kubernetes
            secrets = sm.read_secrets(secretdef.get("secret_name"), secretdef.get("namespace"),
                                  secretdef.get("read_type"))
        elif secretcfg.get("SOURCE") == "KUBEVAULT":
            
               secrets = sm.read_secrets(secretdef.get("secret_name"), secretdef.get("namespace"), 
                                  secretdef.get("read_type"), secretdef.get("secret_key"), 
                                  secretdef.get("transit_key"))
        else:
            print(f"Unknown secret source: {secretcfg.get('SOURCE')}")
            return None
        del sm  # Clean up the SecretManager instance
        return secrets

    def connect_redis(self):
        if self.secrets['rpass'] == 'None':
            r = redis.Redis(host=self.secrets['rhost'], port=6379, db=0, decode_responses=True)
        else:
            r = redis.Redis(host=self.secrets['rhost'], port=6379, db=0, decode_responses=True, 
                                 password=self.secrets['rpass'])
        return r
    
    def update(self): # really must be overridden...
        """ ... """
        print(f"{type(self).__name__} updated.")

    def check(self, now: float):
        """ ... """
        if self.last_update == 0 or now - self.last_update > self.update_period:
            self.last_update = now
            print(f'Updating {type(self).__name__}...')
            self.update()
            if self.r:
                self.r.publish('update', self.type)
            print(f"{arrow.now().to(self.timezone).format('MM/DD/YYYY h:mm:ss A ZZZ')}: " \
                  f"{type(self).__name__} updated.")

    def run(self):
        """ ... """
        # Write Startup record to database
        tnow = arrow.now()
        data = {}
        data['type']   = f'{self.type}-Server'
        data['updated'] = tnow.to(self.timezone).format('MM/DD/YYYY h:mm A ZZZ')
        data['valid']   = tnow.to(self.timezone).format('MM/DD/YYYY h:mm:ss A ZZZ')
        data['values'] = {}
        self.dba.write(data)

        if self.prod:
            HOST = '0.0.0.0'
            PORT = 10255

            class MyTCPHandler(socketserver.BaseRequestHandler):
                # Socket handler for liveness probe
                def handle(self):
                    self.data = self.request.recv(1024).strip()
                    print('Health Check...')
                    self.request.sendall(self.data.upper())

            with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
                server.timeout = 0.1
                while True:
                    now = time.monotonic()
                    self.check(now)
                    server.handle_request()
                    time.sleep(0.9)
        else:
            while True:
                    now = time.monotonic()
                    self.check(now)
                    # server.handle_request()
                    time.sleep(0.95)


    def fetch(self, url: str, name: str, now: str, auth: str=None, headers: str=None): 
        """ ... """
        with self.rsess as sess:
            try:
                if auth is None and headers is None:
                    response = sess.get(url,timeout=(5,15))
                elif headers is None:
                    response = sess.get(url,timeout=(5,15),auth=auth)
                else:
                    response = sess.get(url,timeout=(5,15),headers=headers)
                response.raise_for_status()
            except HTTPError as http_err:
                print(f'({name}) HTTP error occurred: {http_err} @ {now}')
                return None
            except ConnectionError as http_err:
                print(f'({name}) HTTP error occurred: {http_err} @ {now}')
                return None
            # except Exception as err:
            #     print(f'({name}) Other error occurred: {err} @ {now}')
            #     return None
            else:
                try:
                    if self.output:
                        print(response)
                        print(f'apparent_encoding: [{response.apparent_encoding}]')
                        print(f'content: [{response.content}]')
                        print(f'   text: [{response.text}]')
                    values = response.json()
                except json.decoder.JSONDecodeError:
                    raise
                else:
                    return values # response.json()

    def fetch_raw(self, url: str, name: str, now: str):
        """ required for Garmin server which expects an XML response instead of a JSON one """
        with self.rsess as sess:
            try:
                response = sess.get(url,timeout=(5,15))
                response.raise_for_status()
            except HTTPError as http_err:
                print(f'({name}) HTTP error occurred: {http_err} @ {now}')
                return None
            except ConnectionError as http_err:
                print(f'({name}) HTTP error occurred: {http_err} @ {now}')
                return None
            # except Exception as err:
            #     print(f'({name}) Other error occurred: {err} @ {now}')
            #     return None
            return response

    def now_str(self, now: arrow, secs: bool):
        """ ... """
        if secs:
            return now.format('MM/DD/YYYY h:mm:ss A ZZZ')

        return now.format('MM/DD/YYYY h:mm A ZZZ')
    
