from flask import Flask, request, jsonify
from utilities import *
from config import *
import sys, os

app = Flask(__name__)

# The API endpoints immediately redirect to their handlers, passing them the
# JSON request object

# No changes required in this file (yet)

@app.route('/user/insert', methods=['POST'])
def user_insert_callback():
    req = request.get_json()
    return userInsertHandle(req)

@app.route('/user/delete', methods=['POST'])
def user_delete_callback():
    req = request.get_json()
    return userDeleteHandle(req)

@app.route('/user/query', methods=['POST'])
def user_query_callback():
    req = request.get_json()
    return userQueryHandle(req)

@app.route('/user/depart', methods=['POST'])
def user_depart_callback():
    req = request.get_json()
    return userDepartHandle(req)

@app.route('/user/overlay', methods=['POST'])
def user_overlay_callback():
    req = request.get_json()
    return userOverlayHandle(req)

@app.route('/master/join', methods=['POST'])
def master_join_callback():
    req = request.get_json()
    return masterJoinHandle(req)

@app.route('/master/depart', methods=['POST'])
def master_depart_callback():
    req = request.get_json()
    return masterDepartHandle(req)

@app.route('/node/updatePeerList', methods=['POST'])
def node_updatePeerList_callback():
    req = request.get_json()
    return nodeUpdatePeerListHandle(req)

@app.route('/node/query', methods=['POST'])
def node_query_callback():
    req = request.get_json()
    return nodeQueryHandle(req)

@app.route('/node/insert', methods=['POST'])
def node_insert_callback():
    req = request.get_json()
    return nodeInsertHandle(req)

@app.route('/node/delete', methods=['POST'])
def node_delete_callback():
    req = request.get_json()
    return nodeDeleteHandle(req)


if __name__ == '__main__':
    # run app in debug mode on port 5000
    print("\n")

    if len(sys.argv) < 3:
        print("Tell me the port, e.g. -p 5000")
        exit(0)

    # get the port from the command line
    if sys.argv[1] in ("-p", "-P"):
        KARNAK_PORT = sys.argv[2]

    # get the ip from the command line
    KARNAK_IP = os.popen('ip addr show ' + NETIFACE +
    ' | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()

    if KARNAK_IP == KARNAK_MASTER_IP and KARNAK_PORT == KARNAK_MASTER_PORT:

        # for the master node
        print("I am the master node with ip: " + KARNAK_IP + " and port: " +
              KARNAK_PORT)

        MASTER_ID = hash(KARNAK_MASTER_IP + KARNAK_MASTER_PORT)
        print("My id is: " + MASTER_ID)

        SELF_MASTER = True

        # Master is the first one to enter the list
        # we need this list to create the PEERS_LIST dynamically
        NODES_LIST = {"nid":MASTER_ID, "ip":KARNAK_MASTER_IP,
                      "port":KARNAK_MASTER_PORT}

    else:

        SELF_MASTER = False
        print("I am a normal Node with ip: " + KARNAK_IP + " and port "+
              KARNAK_PORT)

        KARNAK_ID = hash(KARNAK_IP + KARNAK_PORT)
        print("My id is: " + KARNAK_ID)
        print("\nJoing the chord...")

        try:
        	response = requests.post(HTTP + KARNAK_MASTER_IP + ":" +
                                     config.KARNAK_MASTER_PORT + "/master/join",
                                     data = {"nid":KARNAK_ID, "ip":KARNAK_IP,
                                             "port":KARNAK_PORT})
        	if response.status_code == 200:
        		print(response.text)
        	else:
        		print("Something went wrong!!  status code: " +
                 response.status.code)
        		print("\nexiting...")
        		exit(0)
        except:
        	print("\nSomething went wrong!! (check if bootstrap is up and running)")
        	print("\nexiting...")
        	exit(0)

    print("\n")

    app.run(debug = True, port = KARNAK_PORT, host = KARNAK_IP,
     use_reloader=False)
