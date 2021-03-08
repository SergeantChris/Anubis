from calls import *
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

def userDepartHandle(req):
    return 'depart'

def userOverlayHandle(req):
    return 'overlay'

def masterJoinHandle(req):
    return 'master join'

def masterDepartHandle(req):
    return 'depart'

def nodeUpdatePeerListHandle(req):
    return 'peer'

def nodeQueryHandle(req):
    return 'query'

def nodeInsertHandle(req):
    return 'insert'

def nodeDeleteHandle(req):
    return 'delete'

def hash(key):
	return hashlib.sha1(key.encode('utf-8')).hexdigest()
