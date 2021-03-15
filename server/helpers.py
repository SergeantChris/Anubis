from flask import request
import hashlib
from pprint import pprint
from calls import *
import globals


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


def add_to_global_SONG_DICT(req):
    """
    Inserts (or updates) the corresponding song inside the global song dictionary
    :param req: The song
    :return: None
    """
    globals.SONG_DICT[req['key']] = {
        'sid': req['sid'],
        'key': req['key'],
        'value': req['value']
    }
    print(f'Added {req["key"]} to my global song list:')
    pprint(globals.SONG_DICT)


def notify_requester(req, req_type, status, data={}):
    requester_ip = req["requester_ip"]
    requester_port = req["requester_port"]
    param = {
        'request': req_type,
        'status': status,
    }
    if req_type == 'query' and status == 'ok' and req['song_name'] == '*':
        param['data'] = str(req)
        param['song_name'] = req['song_name']
    elif req_type == 'query' and status == 'ok':
        param['sender_id'] = data['sender_id']
        param['sender_ip'] = data['sender_ip']
        param['sender_port'] = data['sender_port']
        param['sid'] = data['song']['sid']
        param['key'] = data['song']['key']
        param['song_name'] = data['song']['key']
        param['value'] = data['song']['value']
    remoteNodeReceive(requester_ip, requester_port, param)


def check_primary_responsibility(sid):
    """
    :param sid: The song ID to check primary responsiblity for
    :return: The check status
    """
    return ((sid <= globals.KARNAK_ID == globals.PEER_LIST[0]['nid'])
            or (sid > globals.PEER_LIST[-1]['nid'] and globals.KARNAK_ID == globals.PEER_LIST[0]['nid'])
            or (globals.KARNAK_ID >= sid > globals.PREV_PEER['nid']))


def delete_song(req):
    if req['key'] in globals.SONG_DICT:
        globals.SONG_DICT.pop(req['key'])
        print(f'Deleted {req["key"]} from my global song list:')
        pprint(globals.SONG_DICT)


def query_thread(req):
    response = remoteNodeQuery(globals.KARNAK_IP, globals.KARNAK_PORT, req)
    return response.text


def insert_thread(req):
    response = remoteNodeInsert(globals.KARNAK_IP, globals.KARNAK_PORT, req)
    return response.text


def delete_thread(req):
    response = remoteNodeDelete(globals.KARNAK_IP, globals.KARNAK_PORT, req)
    return response.text


def append_request_personal_info(req):
    req["requester"] = globals.KARNAK_ID
    req["requester_ip"] = globals.KARNAK_IP
    req["requester_port"] = globals.KARNAK_PORT
