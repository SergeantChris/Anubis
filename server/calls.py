import requests
from config import *


# These functions are just wrappers to frequently used API calls for network communication

def remoteNodeUpdatePeerList(ip, port, req):
    return requests.post(HTTP + ip + ':' + port + '/node/updatePeerList', req)

def remoteNodeQuery(ip, port, req):
    return requests.post(HTTP + ip + ':' + port + '/node/query', req)

def remoteNodeInsert(ip, port, req):
    return requests.post(HTTP + ip + ':' + port + '/node/insert', req)

def remoteNodeDelete(ip, port, req):
    return requests.post(HTTP + ip + ':' + port + '/node/delete', req)
