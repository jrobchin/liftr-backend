import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/app.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)
import random
import json
from typing import Dict
import functools

from flask import Flask, request, send_from_directory, render_template, g
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo

from constants import LETTERS
from messages import response_message
from sessions import Client, Machine, MobileApp, with_session, sess_manager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/liftr'
# mongo = PyMongo(app)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('app.html')

@app.route('/debug')
def debug():
    return render_template(
        'debug.html',
        sessions=sess_manager.sessions
    )

@socketio.on('connect')
def connect_handler():
    logger.debug(f"connection from sid: {request.sid} ip: {request.remote_addr}")
    return response_message(message="Hello World")

@socketio.on('disconnect')
def disconnect_handler():
    logger.debug(f"disconnect from sid: {request.sid}")
    # TODO: add disconnect handling

@socketio.on('register_machine')
def handle_register_machine(data):
    logger.debug(f"register_machine - sid: {request.sid} data: {data}")
    session = sess_manager.create_session()
    
    machine = Machine(request.sid, session)
    sess_manager.add_client(session, machine)
    return response_message(
        message="Successfully registered",
        data={
            's_key': session.s_key
        }
    )

@socketio.on('register_app')
def handle_register_app(data):
    logger.debug(f"register_app - sid: {request.sid} data: {data}")
    try:
        s_key = int(data['s_key'])
        session = sess_manager.sessions.get(s_key, None)

        if session is not None:
            mobile_app = MobileApp(request.sid, session)
            sess_manager.add_client(session, mobile_app)

            session.emit_machine('start_session')

            return response_message(
                message="Successfully registered"
            )
        else:
            return response_message(
                success=False,
                error="No session with key"
            )
    except ValueError:
        return response_message(
            success=False,
            error="Session key must be a 4 digit integer"
        )

@socketio.on('start_session')
@with_session
def handle_start_session():
    logger.debug(f"start_session - client: {g.client} session: {g.client.session}")
    c: Client = g.client
    s: Session = c.session

    if isinstance(g.client, MobileApp):
        s.emit_machine('start_session')

@socketio.on('select_exercise')
@with_session
def handle_select_exercise(data):
    logger.debug(f"select_exercise - client: {g.client} session: {g.client.session} data: {data}")
    if isinstance(g.client, MobileApp):
        g.session.emit_machine('select_exercise', {
            "exercise": data["exercise"]
        })

@socketio.on('start_exercise')
@with_session
def handle_start_exercise(data):
    logger.debug(f"start_exercise - client: {g.client} session: {g.client.session} data: {data}")
    if isinstance(g.client, MobileApp):
        g.session.emit_machine('start_exercise', {
            "reps": data["reps"]
        })

@socketio.on('make_critique')
@with_session
def handle_make_critique(data):
    logger.debug(f"make_critique - client: {g.client} session: {g.client.session} data: {data}")
    # mongo.db.critiques.insert_one({
    #     "exercise": data["exercise"],
    #     "caption": data["caption"],
    #     "image": data["image"]
    # })

    g.session.emit_app('update_reps', { "reps": 2000 })
    g.session.emit_app('make_critique', data)

@socketio.on('update_reps')
@with_session
def handle_start_exercise(data):
    logger.debug(f"update_reps - client: {g.client} session: {g.client.session} data: {data}")
    if isinstance(g.client, Machine):
        g.session.emit_app('update_reps', {
            "reps": data["reps"]
        })


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True, log_output=True)