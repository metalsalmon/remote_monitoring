from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")


@socketio.on('connect')
def on_connect():
    print(f'[SocketIO]: Client successfully connected.')


@socketio.on('disconnect')
def on_disconnect():
    print(f'[SocketIO]: Client successfully disconnected.')


@socketio.on('callback')
def on_callback(msg):
    print(f'[SocketIO]: ACK: {msg}')

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)