from calls import *
from config import *
import globals
import hashlib


# The following functions are the handlers for API calls.
# They use functions defined in calls.py accordingly, with respect to Chord protocol

# TODO: define the logic of each handler for user/network requests

def userInsertHandle(req):
    return 'insert'

def userDeleteHandle(req):
    return 'delete'

def userQueryHandle(req):
    return 'query'

def userDepartHandle():
    depart = globals.KARNAK_ID
    new_list = [node for node in globals.PEER_LIST if node["nid"] != depart]  # inefficient
    requests.post(HTTP + KARNAK_MASTER_IP + ':' + KARNAK_MASTER_PORT + '/master/depart', {"new_list": str(new_list)})
    return 'informed master'

def userOverlayHandle():
    return str(globals.PEER_LIST)

def masterJoinHandle(req):
    prev_list = globals.PEER_LIST.copy()
    globals.PEER_LIST.append(req)
    globals.PEER_LIST.sort(key=lambda i: (i["nid"]))
    for peer in prev_list:
        remoteNodeUpdatePeerList(peer["ip"], peer["port"], {"new_list": str(globals.PEER_LIST)})
    return str(globals.PEER_LIST)

def masterDepartHandle(req):
    for peer in globals.PEER_LIST:
        remoteNodeUpdatePeerList(peer["ip"], peer["port"], req)
    return 'departed'

def nodeUpdatePeerListHandle(req):
    globals.PEER_LIST = list(eval(req["new_list"]))
    return 'updated peer list'

def nodeQueryHandle(req):
    return 'query'

def nodeInsertHandle(req):
    return 'insert'

def nodeDeleteHandle(req):
    return 'delete'

def hash(key):
    return hashlib.sha1(key.encode('utf-8')).hexdigest()
