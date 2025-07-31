import os
import glob
import subprocess
import time
import pyautogui
from flask import Flask
import zmq
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

RECORDINGS_DIR = '/home/rounak/recordings'

def get_pupil_remote():
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect('tcp://127.0.0.1:50020')
    return socket

def get_latest_recording_path(base_path=RECORDINGS_DIR):
    # Find the most recent dated folder
    dated_dirs = sorted(glob.glob(os.path.join(base_path, "*")), key=os.path.getmtime)
    if not dated_dirs:
        return None
    latest_date_dir = dated_dirs[-1]

    # Now find the last recording in that folder (like 001, 002)
    session_dirs = sorted(glob.glob(os.path.join(latest_date_dir, "*")), key=os.path.getmtime)
    if not session_dirs:
        return None
    return session_dirs[-1]

# def export_recording(recording_path):
#     try:
#         print(f"Exporting from: {recording_path}")
#         subprocess.run([
#             "pupil_player",
#             "--headless",
#             "--recording", recording_path,
#             "--plugins", "export_recording"
#         ], check=True)
#         return True, f"Export complete for {recording_path}"
#     except subprocess.CalledProcessError as e:
#         return False, str(e)

def export_recording(recording_path):
    try:
        print(f"Launching Pupil Player for export: {recording_path}")
        
        # Launch the GUI version of Pupil Player
        subprocess.Popen(["pupil_player", recording_path])

        # Wait enough time for it to load completely
        time.sleep(8)

        # Simulate pressing "e" to trigger export
        pyautogui.press('e')
        print("Export triggered via 'e' key")

        # Optional: Wait for export to finish (e.g., wait 10–20 seconds)
        time.sleep(15)

        return True, f"Export triggered successfully for {recording_path}"
    except Exception as e:
        return False, str(e)




@app.route('/start-recording', methods=['POST'])
def start_recording():
    try:
        pupil_remote = get_pupil_remote()
        pupil_remote.send_string('R')  # Start recording
        response = pupil_remote.recv_string()
        return {'status': 'ok', 'response': response}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/stop-recording', methods=['POST'])
def stop_recording():
    try:
        time.sleep(5)  # Optional delay
        pupil_remote = get_pupil_remote()
        pupil_remote.send_string('r')  # Stop recording
        response = pupil_remote.recv_string()

        # Get latest recording and export it
        latest_path = get_latest_recording_path()
        if not latest_path:
            return {'status': 'error', 'message': 'Recording folder not found'}

        success, msg = export_recording(latest_path)
        if not success:
            return {'status': 'error', 'message': msg}

        return {
            'status': 'ok',
            'recording_path': latest_path,
            'export_status': msg
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    app.run(port=8000)
