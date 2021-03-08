import requests
from config import *

# These functions are just wrappers to frequently used API calls for network communication

def remoteNodeUpdatePeerList(list):
    # list is a list with 3 dictionaries: prev, node, next
    ip = list[1]['ip']
    port = list[1]['port']
    if len(list) > 2:
        req = {"previous": list[0], "next": list[2]}
    else:
        req = {"previous": list[0], "next": list[0]}
    x = requests.post('http://' + ip + ':' + port + '/node/updatePeerList', req)
    return x

def remoteNodeQuery(ip, req):
    x = requests.post('http://' + ip + ':' + KARNAK_PORT + 'node/query', json=req)
    return x

def remoteNodeInsert(ip, req):
    x = requests.post('http://' + ip + ':' + KARNAK_PORT + 'node/insert', json=req)
    return x

def remoteNodeDelete(ip, req):
    x = requests.post('http://' + ip + ':' + KARNAK_PORT + 'node/delete', json=req)
    return x
