from flask import Flask, request
from utilities import *
from config import *
import config
import globals
import sys
import os
import threading
import time
import signal

app = Flask(__name__)

# The API endpoints immediately redirect to their handlers, passing them the
# dict request object
@app.route('/user/insert', methods=['POST'])
def user_insert_callback():
    req = request.form.to_dict()
    return userInsertHandle(req)

@app.route('/user/delete', methods=['POST'])
def user_delete_callback():
    req = request.form.to_dict()
    return userDeleteHandle(req)

@app.route('/user/query', methods=['POST'])
def user_query_callback():
    req = request.form.to_dict()
    return userQueryHandle(req)

@app.route('/user/depart', methods=['POST'])
def user_depart_callback():
    return userDepartHandle()

@app.route('/user/overlay', methods=['POST'])
def user_overlay_callback():
    return userOverlayHandle()

@app.route('/master/join', methods=['POST'])
def master_join_callback():
    if globals.SELF_MASTER:
        req = request.form.to_dict()
        return masterJoinHandle(req)
    else:
        raise ConnectionError

@app.route('/master/depart', methods=['POST'])
def master_depart_callback():
    if globals.SELF_MASTER:
        req = request.form.to_dict()
        return masterDepartHandle(req)
    else:
        raise ConnectionError

@app.route('/node/updatePeerList', methods=['POST'])
def node_updatePeerList_callback():
    req = request.form.to_dict()
    return nodeUpdatePeerListHandle(req)

@app.route('/node/query', methods=['POST'])
def node_query_callback():
    req = request.form.to_dict()
    return nodeQueryHandle(req)

@app.route('/node/insert', methods=['POST'])
def node_insert_callback():
    req = request.form.to_dict()
    return nodeInsertHandle(req)

@app.route('/node/delete', methods=['POST'])
def node_delete_callback():
    req = request.form.to_dict()
    return nodeDeleteHandle(req)

@app.route('/node/receive', methods=['POST'])
def node_receive_callback():
    req = request.form.to_dict()
    return nodeReceiveHandle(req)


def net_init():
    # get the port from the command line
    time.sleep(1)
    port = sys.argv[2]
    # get the ip from the command line
    ip = os.popen('ip addr show ' + NETIFACE +
                  ' | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\''
                  ).read().strip()
    globals.KARNAK_PORT = port
    globals.KARNAK_IP = ip
    globals.SONG_DICT = {}
    globals.DOWNLOADED_LIST = {}
    globals.found_it = False
    if ip == KARNAK_MASTER_IP and port == KARNAK_MASTER_PORT:
        globals.SELF_MASTER = True
        # TODO: dynamically retrieve values of -flags and their respective values (based on index within argv)
        if len(sys.argv) < 6 or sys.argv[3] != '-k' or sys.argv[5] not in ('-l', '-e'):
            print('Please specify replication factor, e.g. -k 2')
            print('Please specify replica consistency mode, -l for linearizability, -e for eventual')
            os.kill(os.getpid(), signal.SIGINT)
        config.REP_K = int(sys.argv[4])
        if sys.argv[5] == '-l':
            config.CONSISTENCY_MODE = 'l'
        elif sys.argv[5] == '-e':
            config.CONSISTENCY_MODE = 'e'
        print('I am the master node with ip: ' + ip + ' and port: ' + port)
        globals.KARNAK_ID = hash(KARNAK_MASTER_IP + KARNAK_MASTER_PORT)
        print('My id is: ' + globals.KARNAK_ID)
        print(f'Network is set up with file replication factor k={config.REP_K} '
              f'and {config.CONSISTENCY_MODE} consistency mode')
        if config.CONSISTENCY_MODE == 'l':
            print('Linearizability is implemented via chain replication')
        # Master is the first one to enter the list
        globals.PEER_LIST = [{"nid": globals.KARNAK_ID, "ip": KARNAK_MASTER_IP,
                              "port": KARNAK_MASTER_PORT}]
    else:
        globals.SELF_MASTER = False
        print('I am a normal Node with ip: ' + ip + ' and port ' +
              port)
        globals.KARNAK_ID = hash(ip + port)
        print('My id is: ' + globals.KARNAK_ID)
        join_req = {
            "nid": globals.KARNAK_ID,
            "ip": ip,
            "port": port
        }
        try:
            response = requests.post(HTTP + KARNAK_MASTER_IP + ':' +
                                     KARNAK_MASTER_PORT + '/master/join',
                                     join_req)
            print(response.text)
            if response.status_code == 200:
                print('**Joined Chord**')
            else:
                raise ConnectionRefusedError(f'status code: {response.status_code}')
        except ConnectionRefusedError as e:
            print('\nSomething went wrong, ' + e.args[0])
            print('\nexiting...')
            exit(0)
    print('\n')


def server_run():
    # get the ip from the command line
    if len(sys.argv) < 3 or sys.argv[1] not in ('-p', '-P'):
        print('Tell me the port, e.g. -p 5000')
        # TODO: make pretty :D
        os.kill(os.getpid(), signal.SIGINT)
    port = sys.argv[2]
    ip = os.popen('ip addr show ' + NETIFACE +
                  ' | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\''
                  ).read().strip()
    # run app in debug mode
    app.run(debug=True, host=ip, port=port, use_reloader=False)


if __name__ == '__main__':
    t1 = threading.Thread(target=net_init, args=())
    t2 = threading.Thread(target=server_run, args=())
    t1.start()
    t2.start()
