from flask import Flask, request
from utilities import *
from config import *
import globals
import sys
import os


app = Flask(__name__)

# The API endpoints immediately redirect to their handlers, passing them the
# dict request object

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


if __name__ == '__main__':

    # get the port from the command line
    if len(sys.argv) < 3 or sys.argv[1] not in ('-p', '-P'):
        print('Tell me the port, e.g. -p 5000')
        exit(0)

    port = sys.argv[2]

    # get the ip from the command line
    ip = os.popen('ip addr show ' + NETIFACE +
                  ' | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\''
                  ).read().strip()

    globals.KARNAK_PORT = port
    globals.KARNAK_IP = ip
    globals.SONG_DICT = {}
    globals.DOWNLOADED_LIST = {}

    if ip == KARNAK_MASTER_IP and port == KARNAK_MASTER_PORT:

        # for the master node
        print('I am the master node with ip: ' + ip + ' and port: ' + port)

        globals.KARNAK_ID = hash(KARNAK_MASTER_IP + KARNAK_MASTER_PORT)
        print('My id is: ' + globals.KARNAK_ID)

        globals.SELF_MASTER = True

        # Master is the first one to enter the list
        globals.PEER_LIST = [{"nid": globals.KARNAK_ID, "ip": KARNAK_MASTER_IP,
                              "port": KARNAK_MASTER_PORT}]

    else:

        globals.SELF_MASTER = False
        print('I am a normal Node with ip: ' + ip + ' and port ' +
              port)

        globals.KARNAK_ID = hash(ip + port)
        print('My id is: ' + globals.KARNAK_ID)
        print('\nJoining Chord...')

        join_req = {
            "nid": globals.KARNAK_ID,
            "ip": ip,
            "port": port
        }

        try:
            response = requests.post(HTTP + KARNAK_MASTER_IP + ':' +
                                     KARNAK_MASTER_PORT + '/master/join',
                                     join_req)
            globals.PEER_LIST = list(eval(response.text))
            calculate_neighbors()
            if response.status_code == 200:
                print('I got the response')
            else:
                raise ConnectionRefusedError(f'status code: {response.status_code}')
        except ConnectionRefusedError as e:
            print('\nSomething went wrong, ' + e.args[0])
            print('\nexiting...')
            exit(0)

    print('\n')

    # run app in debug mode
    app.run(debug=True, host=ip, port=port, use_reloader=False)
