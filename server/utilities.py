from helpers import *
import config
import globals
from pprint import pprint
import threading
import time

# The following functions are the handlers for API calls.
# They use functions defined in calls.py accordingly, with respect to Chord protocol

def userInsertHandle(req):
    req["sid"] = hash(req["key"])
    req["requester_id"] = globals.KARNAK_ID
    req["requester_ip"] = globals.KARNAK_IP
    req["requester_port"] = globals.KARNAK_PORT
    req["replicounter"] = config.REP_K-1
    t = threading.Thread(target=insert_thread, args=(req, ))
    t.start()
    while not globals.request_ready:
        time.sleep(0.1)
    globals.request_ready = False
    time.sleep(0.1)

    return "The song is added in the network."\
        if globals.request_result == 'ok'\
        else 'Could not insert'
    t.join()


def userDeleteHandle(req):
    req["sid"] = hash(req["key"])
    req["requester_id"] = globals.KARNAK_ID
    req["requester_ip"] = globals.KARNAK_IP
    req["requester_port"] = globals.KARNAK_PORT
    t = threading.Thread(target=delete_thread, args=(req, ))
    t.start()
    while not globals.request_ready:
        time.sleep(0.1)
    globals.request_ready = False
    time.sleep(0.1)
    return "The song was deleted." \
        if globals.request_result == 'ok' \
        else 'Song not found, thus not deleted.'
    t.join()


def userQueryHandle(req):
    song_name = req["song_name"]
    req["requester_id"] = globals.KARNAK_ID
    req["requester_ip"] = globals.KARNAK_IP
    req["requester_port"] = globals.KARNAK_PORT
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
        return 'Song not found in network'
    t.join()

def userDepartHandle():
    # Only inform master about *who* you are, he will calculate the new list (issue with concurrent departs)
    depart = globals.KARNAK_ID
    requests.post(HTTP + KARNAK_MASTER_IP + ':' + KARNAK_MASTER_PORT + '/master/depart', {'depart_id': depart})
    # has to re-arrange the songs before it goes
    new_owner = globals.NEXT_PEER
    while globals.SONG_DICT:
        song = globals.SONG_DICT.popitem()[1]
        song['requester_ip'] = globals.KARNAK_IP
        song['requester_port'] = globals.KARNAK_PORT
        remoteNodeInsert(new_owner["ip"], new_owner["port"], song)
    print('Rearranged songs before depart, I now own')
    pprint(globals.SONG_DICT)
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
    # new node must be updated first so that it's ready to receive songs
    remoteNodeUpdatePeerList(req["ip"], req["port"], {"new_list": str(globals.PEER_LIST),
                                                      "action": 'join',
                                                      "actor_id": req["nid"]})
    # sends rep_k to new node
    remoteNodeReceive(req["ip"], req["port"], {"request": 'send_rep_info', "k": str(config.REP_K), "mode": config.CONSISTENCY_MODE})
    for peer in prev_list:
        if peer["nid"] != globals.KARNAK_ID:  # master doesn't update itself
            remoteNodeUpdatePeerList(peer["ip"], peer["port"], {"new_list": str(globals.PEER_LIST),
                                                                "action": 'join',
                                                                "actor_id": req["nid"]})
    return "you're in!"


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
                song['requester_ip'] = globals.KARNAK_IP
                song['requester_port'] = globals.KARNAK_PORT
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
    requester = req['requester_id']
    song_name = req['song_name']
    # I just want one specific song
    if song_name != "*":
        # if I have the song
        if song_name in globals.SONG_DICT:
            song = globals.SONG_DICT[song_name]
            # create response object containing both song and my id\
            data = {
                "sender_id": globals.KARNAK_ID,
                "sender_ip": globals.KARNAK_IP,
                "sender_port": globals.KARNAK_PORT,
                "song": song
            }
            notify_requester(req, 'query', 'ok', data)
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


def nodeInsertHandle(req):
    sid = req['sid']
    # TODO: remove metadata before inserting to dict!!!
    if check_primary_responsibility(sid):
        add_to_global_SONG_DICT(req)
        # TODO: notifier must be last node in K field
        notify_requester(req, 'insert', 'ok')
        # if config.CONSISTENCY_MODE == 'l':
        #     # passing request to next if within k-1
        #     if int(req["replicounter"]) > 0:
        #         req["replicounter"] = int(req["replicounter"]) - 1
        #         # TODO:  to be changed after fixing other stuff, currently inserts to itself k times
        #         response = remoteNodeInsert(globals.NEXT_PEER['ip'], globals.NEXT_PEER['port'], req)
        #         return response.text
        #
        return f'The song was added in {config.REP_K} RM nodes'
    # This is never meant to be executed / Insert never fails
    elif req["requester_id"] == globals.NEXT_PEER['nid']:
        notify_requester(req, 'insert', 'error')
    else:
        # passing request to next
        response = remoteNodeInsert(globals.NEXT_PEER['ip'], globals.NEXT_PEER['port'], req)
        return response.text


def nodeDeleteHandle(req):
    sid = req['sid']
    # TODO: what happens with replicas?
    if check_primary_responsibility(sid):
        delete_song(req)
        notify_requester(req, 'delete', 'ok')
    # If request made full circle
    elif req['requester_id'] == globals.NEXT_PEER['nid']:
        notify_requester(req, 'delete', 'error')
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
