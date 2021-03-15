from helpers import *
import config
import globals
from pprint import pprint
import threading
import time

# The following functions are the handlers for API calls.
# They use functions defined in calls.py accordingly, with respect to Chord protocol


def insert_thread(req):
    response = remoteNodeInsert(globals.KARNAK_IP, globals.KARNAK_PORT, req)
    return response.text

def userInsertHandle(req):
    req["sid"] = hash(req["key"])
    append_request_personal_info(req)
    t = threading.Thread(target=insert_thread, args=(req, ))
    t.start()
    while not globals.request_ready:
        time.sleep(0.1)
    globals.request_ready = False
    time.sleep(0.1)
    return {'msg': 'The song is added in the network.'}\
        if globals.request_result == 'ok'\
        else {'msg': 'Could not insert'}
    t.join()


def delete_thread(req):
    response = remoteNodeDelete(globals.KARNAK_IP, globals.KARNAK_PORT, req)
    return response.text

def userDeleteHandle(req):
    req["sid"] = hash(req["key"])
    append_request_personal_info(req)
    t = threading.Thread(target=delete_thread, args=(req, ))
    t.start()
    while not globals.request_ready:
        time.sleep(0.1)
    globals.request_ready = False
    time.sleep(0.1)
    return {'msg': 'The song was deleted.'} \
        if globals.request_result == 'ok' \
        else {'msg': 'Song not found, thus not deleted.'}
    t.join()


def query_thread(req):
    response = remoteNodeQuery(globals.KARNAK_IP, globals.KARNAK_PORT, req)
    return response.text

def userQueryHandle(req):
    song_name = req["song_name"]
    append_request_personal_info(req)
    t = threading.Thread(target=query_thread, args=(req, ))
    t.start()
    while not globals.request_ready:
        time.sleep(0.1)
    globals.request_ready = False
    time.sleep(0.1)
    if globals.request_result == 'ok':
        if song_name == "*":
            return eval(globals.ALL_SONGS)
        else:
            return globals.DOWNLOADED_LIST[song_name]
    else:
        return {'msg': 'Song not found in network'}
    t.join()


def userDepartHandle():
    # Only inform master about *who* you are, he will calculate the new list (issue with concurrent departs)
    requests.post(HTTP + KARNAK_MASTER_IP + ':' + KARNAK_MASTER_PORT + '/master/depart', {'nid': globals.KARNAK_ID,
                                                                                          'ip': globals.KARNAK_IP,
                                                                                          'port': globals.KARNAK_PORT})
    # has to re-arrange the songs before it goes
    new_owner = globals.NEXT_PEER
    while globals.SONG_DICT:
        song = globals.SONG_DICT.popitem()[1]
        song["requester_id"] = globals.NEXT_PEER['nid']
        song['requester_ip'] = globals.NEXT_PEER['ip']
        song['requester_port'] = globals.NEXT_PEER['port']
        remoteNodeDelete(globals.NEXT_PEER['ip'],
                         globals.NEXT_PEER['port'],
                         song)
        remoteNodeInsert(new_owner["ip"], new_owner["port"], song)
    print('Rearranged songs before depart, I now own')
    pprint(globals.SONG_DICT)
    shutdown_server()
    return {'msg': 'Departing & Shutting down...'}


def userOverlayHandle():
    return {
        "peers_list": globals.PEER_LIST,
        "prev_peer": globals.PREV_PEER,
        "next_peer": globals.NEXT_PEER
    }


def masterJoinHandle(req):
    globals.PEER_LIST.append(req)
    globals.PEER_LIST.sort(key=lambda i: (i["nid"]))
    calculate_neighbors()
    # new node must be updated first so that it's ready to receive songs
    remoteNodeUpdatePeerList(req["ip"], req["port"], {"new_list": str(globals.PEER_LIST),
                                                      "action": 'join',
                                                      "actor_id": req["nid"]})
    # sends rep_k to new node
    remoteNodeReceive(req["ip"], req["port"], {"request": 'send_rep_info', "k": str(config.REP_K), "mode": config.CONSISTENCY_MODE})
    copy = globals.PEER_LIST.copy()
    le_list = copy[:copy.index(req)][::-1] + copy[copy.index(req):][::-1]
    le_list.pop()
    for peer in le_list:
        if peer["nid"] != globals.KARNAK_ID:  # master doesn't update itself
            remoteNodeUpdatePeerList(peer["ip"], peer["port"], {"new_list": str(globals.PEER_LIST),
                                                                "action": 'join',
                                                                "actor_id": req["nid"]})
    return "you're in!"


def masterDepartHandle(req):
    copy = globals.PEER_LIST.copy()
    le_list = copy[:copy.index(req)][::-1] + copy[copy.index(req):][::-1]
    le_list.pop()
    # Update master's global peer list
    globals.PEER_LIST = [node for node in globals.PEER_LIST if node["nid"] != req["nid"]]
    globals.PEER_LIST.sort(key=lambda i: (i["nid"]))
    calculate_neighbors()
    for peer in le_list:
        if peer["nid"] != globals.KARNAK_ID:  # master doesn't update itself
            remoteNodeUpdatePeerList(peer["ip"], peer["port"], {"new_list": str(globals.PEER_LIST),
                                                                "action": 'depart',
                                                                "actor_id": req["nid"]})
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
                append_request_personal_info(song)
                remoteNodeDelete(globals.NEXT_PEER['ip'], globals.NEXT_PEER['port'], song)
                # songs are also appended concurrently to SONG_DICT by following insert, so song won't
                # necessarily still be the last one for popitem
                remoteNodeInsert(new_owner["ip"], new_owner["port"], song)
            print('Rearranged songs after join, I now own')
            pprint(globals.SONG_DICT)
    print('Updated my peer list: ')
    pprint(globals.PEER_LIST)
    return 'updated peer list'


def nodeQueryHandle(req):
    requester = req['requester_id']
    song_name = req['song_name']
    # I just want one specific song
    if song_name != "*":
        # if I have the song
        if song_name in globals.SONG_DICT:
            if config.CONSISTENCY_MODE == 'l':
                if check_primary_responsibility(globals.SONG_DICT[song_name]['sid']):
                    req['replicounter'] = config.REP_K-1
                    response = remoteNodeQuery(globals.NEXT_PEER['ip'],
                                               globals.NEXT_PEER['port'],
                                               req)
                    return response.text
                elif 'replicounter' in req:
                    # passing request to next if within k-1
                    req["replicounter"] = int(req["replicounter"]) - 1
                    if int(req["replicounter"]) > 0:
                        response = remoteNodeQuery(globals.NEXT_PEER['ip'],
                                                   globals.NEXT_PEER['port'],
                                                   req)
                        return response.text
                    # am k-th node
                    else:
                        make_song_response(song_name, req)
                        return 'ok'
                else:
                    remoteNodeQuery(globals.NEXT_PEER['ip'],
                                    globals.NEXT_PEER['port'],
                                    req)
                    return "it's not time yet"
            elif config.CONSISTENCY_MODE == 'e':
                make_song_response(song_name, req)
                return 'ok'
        # if the request made a full cycle
        elif requester == globals.NEXT_PEER['nid']:
            notify_requester(req, 'query', 'error')
            return 'error'
        # if I don't have the song
        else:
            response = remoteNodeQuery(globals.NEXT_PEER['ip'],
                                       globals.NEXT_PEER['port'],
                                       req)
            return response.text
    # I want to know all songs (every song per node)
    else:
         # if the request made a full cycle
         if requester == globals.NEXT_PEER["nid"]:
            req[globals.KARNAK_ID] = str(globals.SONG_DICT)

            notify_requester(req, 'query', 'ok')
            return 'ok'
         # if you are a regular node
         else:
            # Append your songs under your unique key
            req[globals.KARNAK_ID] = str(globals.SONG_DICT)
            remoteNodeQuery(globals.NEXT_PEER['ip'],
                            globals.NEXT_PEER['port'],
                            req)
            return 'ok'


def go_send_yourself(req):
    time.sleep(5)  # simulating wait for enough network bandwidth
    # Time to send update to replica nodes!
    if int(req["replicounter"]) > 0:
        response = remoteNodeInsert(globals.NEXT_PEER['ip'], globals.NEXT_PEER['port'], req)
        return response.text
    return 'ok'

def nodeInsertHandle(req):
    if check_primary_responsibility(req['sid']):
        add_to_global_SONG_DICT(req)
        req["replicounter"] = config.REP_K - 1
        if config.CONSISTENCY_MODE == 'l':
            if int(req["replicounter"]) > 0:
                response = remoteNodeInsert(globals.NEXT_PEER['ip'], globals.NEXT_PEER['port'], req)
                return response.text
            return 'ok'
        elif config.CONSISTENCY_MODE == 'e':
            t = threading.Thread(target=go_send_yourself, args=(req,))
            t.start()
            notify_requester(req, 'insert', 'ok')
            return 'ok'
    elif 'replicounter' in req:
        add_to_global_SONG_DICT(req)
        # passing request to next if within k-1
        req["replicounter"] = int(req["replicounter"]) - 1
        if int(req["replicounter"]) > 0:
            response = remoteNodeInsert(globals.NEXT_PEER['ip'], globals.NEXT_PEER['port'], req)
            return response.text
        # am k-th node
        else:
            notify_requester(req, 'insert', 'ok')
            return 'The song was added in all RM nodes'
    else:
        # passing request to next
        response = remoteNodeInsert(globals.NEXT_PEER['ip'], globals.NEXT_PEER['port'], req)
        return response.text


def nodeDeleteHandle(req):
    delete_song(req)
    # If my next is requester
    if req['requester_id'] == globals.NEXT_PEER['nid']:
        notify_requester(req, 'delete', 'ok')
    # If my next is not requester
    else:
        response = remoteNodeDelete(globals.NEXT_PEER['ip'],
                                    globals.NEXT_PEER['port'],
                                    req)
        return response.text
    return 'The song is not longer in the network'


def nodeReceiveHandle(req):
    req_type = req["request"]
    if req_type == 'query':
        if req['status'] == 'ok':
            if req['song_name'] == '*':
                globals.ALL_SONGS = req['data']
            else:
                globals.DOWNLOADED_LIST[req['key']] = req
    elif req_type == 'send_rep_info':
        config.REP_K = int(req["k"])
        config.CONSISTENCY_MODE = req["mode"]
    if req_type in ['insert', 'query', 'delete']:
        globals.request_ready = True
        globals.request_result = req['status']
    return 'thamk you'
