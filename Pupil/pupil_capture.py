from flask import Flask
import zmq
import time
from flask_cors import CORS



app = Flask(__name__)
CORS(app)
# Helper function to create a socket
def get_pupil_remote():
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect('tcp://127.0.0.1:50020')
    return socket

@app.route('/start-recording', methods=['POST'])
def start_recording():
    try:
        pupil_remote = get_pupil_remote()
        pupil_remote.send_string('R')  # Start recording
        response = pupil_remote.recv_string()
        return {'status': 'ok', 'response': response}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/stop-recording', methods=['POST'])  # <-- fixed 'methods'
def stop_recording():
    try:
        time.sleep(5)  # Optional delay
        pupil_remote = get_pupil_remote()
        pupil_remote.send_string('r')  # Stop recording
        response = pupil_remote.recv_string()
        return {'status': 'ok', 'response': response}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    app.run(port=8000)
