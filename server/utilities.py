from calls import *
import hashlib


# The following functions are the handlers for API calls.
# They use functions defined in calls.py accordingly, with respect to Chord protocol

# TODO: define the logic of each handler for user/network requests

def userInsertHandle(req):
    return 'todo'

def userDeleteHandle(req):
    return 'todo'

def userQueryHandle(req):
    return 'todo'

def userDepartHandle(req):
    return 'todo'

def userOverlayHandle(req):
    return 'todo'

def masterJoinHandle(req):
    return 'todo'

def masterDepartHandle(req):
    return 'todo'

def nodeUpdatePeerListHandle(req):
    return 'todo'

def nodeQueryHandle(req):
    return 'todo'

def nodeInsertHandle(req):
    return 'todo'

def nodeDeleteHandle(req):
    return 'todo'

def hash(key):
	return hashlib.sha1(key.encode('utf-8')).hexdigest()
