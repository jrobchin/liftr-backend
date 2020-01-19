from flask import Flask, escape, request, send_from_directory, json
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

class Client:
    def __init__(self, key):
        self.key = key

class Machine:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class App:
    def __init__(self, key):
        super().__init__(**kwargs)

class Session:
    def __init__(self, session_key):
        self.machine = None
        self.app = None
    
    def _generate_key(self):
        pass

sessions = {}

@app.route('/')
def hello():
    return send_from_directory('./', 'index.html')

@socketio.on('connect')
def connect_handler():
    print('connected', request.sid)

@socketio.on('join')
def handle_join(data):
    print('join')
    if data['client_type'] == 'machine':
        print('machine joined')
    elif data['client_type'] == 'app':
        print('app joined')

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True, log_output=True)