
from flask import Flask, request
from utilities import *
from config import *

app = Flask(__name__)

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
    app.run(debug=True, port=5000)