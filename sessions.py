from typing import Dict
import random
import functools
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/app.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)

from flask import request, g
from flask_socketio import emit

class Client:
    def __init__(self, sid, session, **kwargs):
        self.sid = sid
        self.session = session
    
    def __str__(self):
        return f"<Client sid={self.sid}>"

    def __hash__(self):
        return self.sid

class Machine(Client):
    def __init__(self, sid, session=None, **kwargs):
        super().__init__(sid, session, **kwargs)
    
    def __str__(self):
        return f"<Machine sid={self.sid}>"

class MobileApp(Client):
    def __init__(self, sid, session=None, **kwargs):
        super().__init__(sid, session, **kwargs)
    
    def __str__(self):
        return f"<MobileApp sid={self.sid}>"

class Session:
    def __init__(self, s_key):
        self.s_key = s_key
        self.machine = None
        self.mobile_app = None 
    
    def __str__(self):
        return f"<Session s_key={self.s_key}>"
    
    def __repr__(self):
        return str(self)

    def emit_machine(self, event, data=None, callback=None):
        if self.machine is not None:
            emit(event, data, room=self.machine.sid, callback=callback)

    def emit_app(self, event, data=None, callback=None):
        if self.mobile_app is not None:
            emit(event, data, room=self.mobile_app.sid, callback=callback)

class SessionManager:
    def __init__(self, n_keys=100):
        self._keys = self._generate_keys(n_keys)
        self._key_idx = 0
        self._sessions: Dict[str, Session] = {} # Store sessions by their s_key
        self._clients: Dict[str, Client] = {} # Store clients by their sid
    
    def _generate_keys(self, n_keys):
        keys = list(range(1000, 1001+n_keys))
        random.shuffle(keys)
        return keys
    
    @property
    def keys(self):
        return list(self._sessions.keys())
    
    @property
    def sessions(self):
        return self._sessions

    @property
    def clients(self):
        return self._clients
    
    def create_session(self):
        s_key = self._keys[self._key_idx]
        self._key_idx += 1
        s = Session(s_key)
        self._sessions[s_key] = s
        return s
    
    def add_client(self, session, client):
        self._clients[client.sid] = client
        if isinstance(client, Machine):
            self._sessions[session.s_key].machine = client
        elif isinstance(client, MobileApp):
            self._sessions[session.s_key].mobile_app = client

sess_manager = SessionManager()

def with_session(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        logger.debug(f"getting client with sid: {request.sid}")
        client = sess_manager.clients.get(request.sid, None)
        g.client = client
        g.session = g.client.session
        return func(*args, **kwargs)
    return decorated