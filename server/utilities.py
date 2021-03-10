from calls import *
from config import *
import globals
import hashlib
from flask import request
# The following functions are the handlers for API calls.
# They use functions defined in calls.py accordingly, with respect to Chord protocol

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def userInsertHandle(req):
    return 'insert'

def userDeleteHandle(req):
    return 'delete'

def userQueryHandle(req):
    return 'query'

def userDepartHandle():
    depart = globals.KARNAK_ID
    # Only inform master about who you are, he will calculate the new list (issue with concurrent departs)
    # See below on "masterDepartHandle"
    requests.post(HTTP + KARNAK_MASTER_IP + ':' + KARNAK_MASTER_PORT + '/master/depart', {'depart_id': depart})
    shutdown_server()
    return 'Departing & Shutting down...'

def userOverlayHandle():
    return str(globals.PEER_LIST)

def masterJoinHandle(req):
    prev_list = globals.PEER_LIST.copy()
    globals.PEER_LIST.append(req)
    globals.PEER_LIST.sort(key=lambda i: (i["nid"]))
    for peer in prev_list:
        # Update anyone but master (as master)
        if peer["nid"] != globals.KARNAK_ID:
            remoteNodeUpdatePeerList(peer["ip"], peer["port"], {"new_list": str(globals.PEER_LIST)})
    return str(globals.PEER_LIST)

def masterDepartHandle(req):
    depart = req['depart_id']
    new_list = [node for node in globals.PEER_LIST if node["nid"] != depart]  # inefficient, but good enough :D
    # Update master's global peer list
    globals.PEER_LIST = new_list
    globals.PEER_LIST.sort(key=lambda i: (i["nid"]))
    # Master must not call his own /node/updatePeerList -- Flask will be locked as it is able to process only 1 request
    for peer in globals.PEER_LIST:
        # check if I am not hitting myself (as master)
        if peer["nid"] != globals.KARNAK_ID:
            # give everyone the new list
            remoteNodeUpdatePeerList(peer["ip"], peer["port"], {"new_list": str(globals.PEER_LIST)})
    return 'departed'

def nodeUpdatePeerListHandle(req):
    globals.PEER_LIST = list(eval(req["new_list"]))
    print('Updated my peer list: ', str(globals.PEER_LIST))
    return 'updated peer list'

def nodeQueryHandle(req):
    return 'query'

def nodeInsertHandle(req):
    return 'insert'

def nodeDeleteHandle(req):
    return 'delete'

def hash(key):
    return hashlib.sha1(key.encode('utf-8')).hexdigest()
