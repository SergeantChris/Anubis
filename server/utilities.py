from calls import *
from config import *
import globals
import hashlib
from flask import request
from pprint import pprint
# The following functions are the handlers for API calls.
# They use functions defined in calls.py accordingly, with respect to Chord protocol


def userDepartHandle():
    # Only inform master about *who* you are, he will calculate the new list (issue with concurrent departs) <3
    depart = globals.KARNAK_ID
    requests.post(HTTP + KARNAK_MASTER_IP + ':' + KARNAK_MASTER_PORT + '/master/depart', {'depart_id': depart})
    # has to re-arrange the songs before it goes
    new_owner = globals.NEXT_PEER
    while globals.SONG_DICT:
        song = globals.SONG_DICT.popitem()[1]
        remoteNodeInsert(new_owner["ip"], new_owner["port"], song)
    print('Rearranged songs before depart, I now own')
    pprint(globals.SONG_DICT)
    # shutdown
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
            remoteNodeUpdatePeerList(peer["ip"], peer["port"], {"new_list": str(globals.PEER_LIST),
                                                                "action": 'join',
                                                                "actor_id": req["nid"]})
    return str(globals.PEER_LIST)


def masterDepartHandle(req):
    depart = req["depart_id"]
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
            remoteNodeUpdatePeerList(peer["ip"], peer["port"], {"new_list": str(globals.PEER_LIST),
                                                                "action": 'depart',
                                                                "actor_id": req["depart_id"]})
    return 'departed'


def nodeUpdatePeerListHandle(req):
    globals.PEER_LIST = list(eval(req["new_list"]))
    calculate_neighbors()
    if req["action"] == 'join':
        if globals.PREV_PEER["nid"] == req["actor_id"]:
            new_owner = globals.PREV_PEER
            expendable_copy = globals.SONG_DICT.copy()
            while expendable_copy:
                key, song = expendable_copy.popitem()
                globals.SONG_DICT.pop(key)
                # songs are also appended concurrently to SONG_DICT by following insert, so song won't
                # necessarily still be the last one for popitem
                remoteNodeInsert(new_owner["ip"], new_owner["port"], song)
            print('Rearranged songs after join, I now own')
            pprint(globals.SONG_DICT)
    print('Updated my peer list: ')
    pprint(globals.PEER_LIST)
    return 'updated peer list'


def nodeQueryHandle(req):
    requester = req['requester']
    song_name = req['song_name']

    # if I am the node introducing the request
    if requester == 'you':
        if song_name in globals.SONG_DICT:
            song = globals.SONG_DICT[song_name]
            song['sender_id'] = globals.KARNAK_ID
            song['sender_ip'] = globals.KARNAK_IP
            song['sender_port'] = globals.KARNAK_PORT
            globals.DOWNLOADED_LIST[song_name] = song
            response = type('response', (object, ), {'text': 'ok'})
        else:
            new_req = {
                "song_name": song_name,
                "requester": globals.KARNAK_ID,
                "requester_ip": globals.KARNAK_IP,
                "requester_port": globals.KARNAK_PORT
            }
            response = requests.post(HTTP + globals.NEXT_PEER['ip'] +
                                    ':' + globals.NEXT_PEER['port'] +
                                    '/node/query', new_req)
        # Return to the CLI
        if response.text == 'ok':
            return globals.DOWNLOADED_LIST[song_name]
        else:
            return {
                'msg': response.text
            }
    # if the request made a full cycle
    if requester == globals.KARNAK_ID:
        return 'not found in network'

    # if I have the song
    if song_name in globals.SONG_DICT:
        requester_ip = req['requester_ip']
        requester_port = req['requester_port']
        song = globals.SONG_DICT[song_name]
        # create response object containing both song and my id\
        song['sender_id'] = globals.KARNAK_ID
        song['sender_ip'] = globals.KARNAK_IP
        song['sender_port'] = globals.KARNAK_PORT
        response = requests.post(HTTP + requester_ip +
                                ':' + requester_port +
                                '/node/receive', song)
        if response.text == 'thamk you':
            return 'ok'
        else:
            return 'error while transmitting song'
    # if I don't have the song
    else:
        response = requests.post(HTTP + globals.NEXT_PEER['ip'] +
                                ':' + globals.NEXT_PEER['port'] +
                                '/node/query', req)
        return response.text


def nodeInsertHandle(req):
    sid = req['sid']

    if sid <= globals.KARNAK_ID == globals.PEER_LIST[0]['nid']:
        # i am the node with the smallest id and the song is mine
        add_to_global_SONG_DICT(req)

    elif sid > globals.PEER_LIST[-1]['nid'] and globals.KARNAK_ID == globals.PEER_LIST[0]['nid']:
        # i am the node with the smallest id and the song is mine 2
        add_to_global_SONG_DICT(req)

    elif globals.KARNAK_ID >= sid > globals.PREV_PEER['nid']:
        add_to_global_SONG_DICT(req)

    else:
        # passing request to next
        response = remoteNodeInsert(globals.NEXT_PEER['ip'], globals.NEXT_PEER['port'], req)  # frequently used api call
        return response.text

    return 'The song is added in node with ip ' + globals.KARNAK_IP + 'and port ' + globals.KARNAK_PORT


def nodeDeleteHandle(req):
    sid = req["sid"]
    key = req["key"]

    if sid <= globals.KARNAK_ID and globals.KARNAK_ID == globals.PEER_LIST[0]['nid']:
        # i am the node with the smallest id and I have the song
        delete_song(req)

    elif sid > globals.PEER_LIST[-1]['nid'] and globals.KARNAK_ID == globals.PEER_LIST[0]['nid']:
        # i am the node with the smallest id and I have the song 2
        delete_song(req)

    elif sid <= globals.KARNAK_ID and sid > globals.PREV_PEER['nid']:
        # I have the song
        delete_song(req)

    else:
        # passing the request
        response = requests.post(HTTP + globals.NEXT_PEER['ip'] +
                                 ':' + globals.NEXT_PEER['port'] +
                                 '/node/delete', req)
        return response.text

    return 'The song is not longer in the network'

def nodeReceiveHandle(req):
    globals.DOWNLOADED_LIST[req['key']] = req
    return 'thamk you'



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
    # Find my index in the list
    for i in range(max_index + 1):
        if globals.PEER_LIST[i]['nid'] == globals.KARNAK_ID:
            my_index = i
    if max_index == -1 or my_index == -1:
        raise RuntimeError('Invalid peer list while calculating neighbors')
    # Calculate neighbors
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


def add_to_global_SONG_DICT(req):
    globals.SONG_DICT[req['key']] = req
    print(f'Added {req["key"]} to my global song list:')
    pprint(globals.SONG_DICT)


def delete_song(req):
    globals.SONG_DICT.pop(req['key'])
    print(f'Deleted {req["key"]} from my global song list:')
    pprint(globals.SONG_DICT)


### HELPER FUNCTIONS END ###
