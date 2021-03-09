import requests
from config import *

# These functions are just wrappers to frequently used API calls for network communication

def remoteNodeUpdatePeerList(ip, req):
    x = requests.post('http://' + ip + ':' + KARNAK_PORT + '/node/updatePeerList', json=req)
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
