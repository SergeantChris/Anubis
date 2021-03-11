from calls import *
from config import *
import globals
import hashlib
from flask import request
# The following functions are the handlers for API calls.
# They use functions defined in calls.py accordingly, with respect to Chord protocol

def userInsertHandle(req):

    sid = req['sid']

    if sid <= globals.KARNAK_ID and globals.KARNAK_ID == globals.PEER_LIST[0]['nid']:
        # i am the node with the smallest id and the song is mine
        response = remoteNodeInsert(globals.KARNAK_IP, globals.KARNAK_PORT, req)

    elif sid > globals.PEER_LIST[-1]['nid'] and globals.KARNAK_ID == globals.PEER_LIST[0]['nid']:
        # i am the node with the smallest id and the song is mine 2
        response = remoteNodeInsert(globals.KARNAK_IP, globals.KARNAK_PORT, req)

    elif sid <= globals.KARNAK_ID and sid > globals.PREV_PEER['nid']:
        print("\n yay \n")
        # this song belongs to me
        response = remoteNodeInsert(globals.KARNAK_IP, globals.KARNAK_PORT, req)

    else:
        # passing it
        response = requests.post(HTTP + globals.NEXT_PEER['ip'] +
                                 ':' + globals.NEXT_PEER['port'] +
                                 '/user/insert', req)
    return response.text

def userDeleteHandle(req):
    return 'delete'

def userQueryHandle(req):
    return 'query'

def userDepartHandle():
    # has to re-arrange the songs before it goes
    depart = globals.KARNAK_ID
    # Only inform master about who you are, he will calculate the new list (issue with concurrent departs)
    # See below on "masterDepartHandle"
    requests.post(HTTP + KARNAK_MASTER_IP + ':' + KARNAK_MASTER_PORT + '/master/depart', {'depart_id': depart})
    shutdown_server()
    return 'Departing & Shutting down...'

def userOverlayHandle():
    return {
        "peers_list": globals.PEER_LIST,
        "prev_peer": globals.PREV_PEER,
        "next_peer": globals.NEXT_PEER
    }

def masterJoinHandle(req):
    prev_list = globals.PEER_LIST.copy()
    globals.PEER_LIST.append(req)
    globals.PEER_LIST.sort(key=lambda i: (i["nid"]))
    calculate_neighbors()
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
    calculate_neighbors()
    # Master must not call his own /node/updatePeerList -- Flask will be locked as it is able to process only 1 request
    for peer in globals.PEER_LIST:
        # check if I am not hitting myself (as master)
        if peer["nid"] != globals.KARNAK_ID:
            # give everyone the new list
            remoteNodeUpdatePeerList(peer["ip"], peer["port"], {"new_list": str(globals.PEER_LIST)})
    return 'departed'

def nodeUpdatePeerListHandle(req):
    globals.PEER_LIST = list(eval(req["new_list"]))
    calculate_neighbors()
    print('Updated my peer list: ', str(globals.PEER_LIST))
    return 'updated peer list'

def nodeQueryHandle(req):
    return 'query'

def nodeInsertHandle(req):
    globals.SONG_LIST.append(req)
    print(globals.SONG_LIST)
    return 'The song is added in node with ip ' + globals.KARNAK_IP + "and port " + globals.KARNAK_PORT

def nodeDeleteHandle(req):
    return 'delete'


### HELPER FUNCTIONS START ###

def hash(key):
    return hashlib.sha1(key.encode('utf-8')).hexdigest()

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def calculate_neighbors():
    # Note: Peer list is always shorted
    max_index = len(globals.PEER_LIST) - 1
    my_index = -1
    for i in range(max_index + 1):
        if globals.PEER_LIST[i]['nid'] == globals.KARNAK_ID:
            my_index = i
    if max_index == -1 or my_index == -1:
        raise RuntimeError('Invalid peer list while calculating neighbors')
    prev_index = my_index - 1
    next_index = my_index + 1
    # Edge cases for circular behavior
    if my_index == 0:
        prev_index = max_index
    if my_index == max_index:
        next_index = 0
    globals.PREV_PEER = globals.PEER_LIST[prev_index]
    globals.NEXT_PEER = globals.PEER_LIST[next_index]
    print('Calculated my neighbors: ' + str(prev_index) + ' & ' + str(next_index))

### HELPER FUNCTIONS END ###
