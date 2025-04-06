import shutil
import subprocess
import argparse
import socket
import json
import os
import threading
import gui

parser = argparse.ArgumentParser()

parser.add_argument('-p', '--project', type=str, help='Project directory', required=True)
parser.add_argument('-m', '--micropython', type=str, help='Micropython executable', required=False)

args = parser.parse_args()

if args.micropython == None:
    args.micropython = 'micropython' # Use PATH

if not os.path.exists(os.path.join(args.project, 'main.py')):
    print('No project found')
    exit(1)

emulator_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
emulator_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
emulator_socket.bind(('127.0.0.1', 4455))
emulator_socket.listen()

if os.path.exists('src'):
    shutil.rmtree('src')

shutil.copytree(args.project, 'src')
shutil.copytree('libraries', 'src', dirs_exist_ok=True) # add fake libraries in

os.chdir('src')

micropython_process = subprocess.Popen([args.micropython, 'main.py'])

os.chdir('..')

emulator_conn, addr = emulator_socket.accept()

gui = gui.GUI()

def receive_commands():
    while gui.running:
        try:
            data = json.loads(emulator_conn.recv(1024).decode('utf-8'))
            data_to_send = {'status': 'ok'}
            if not (data['module'] == 'pca9535' and data['command'] == 'get_inputs'):
                #print(data)
                pass
            resp = gui.handle_command(data)
            data_to_send['resp'] = resp
            emulator_conn.send(json.dumps(data_to_send).encode())
        except BrokenPipeError:
            break

    micropython_process.terminate()

threading.Thread(target=receive_commands).start()
gui.gameloop()
