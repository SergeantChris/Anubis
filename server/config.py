# Network variables
from flask import request

LOCAL_MODE = False

KARNAK_MASTER_PORT = '5000'

def REQUEST_PARSER():
    if LOCAL_MODE:
        return request.form.to_dict()
    else:
        return request.get_json()

if LOCAL_MODE:
    KARNAK_MASTER_IP = '127.0.0.1'
    NETIFACE = 'lo'

else:
    NETIFACE = 'ens3'
    KARNAK_MASTER_IP = '217.69.0.179'

HTTP = 'http://'

global REP_K
global CONSISTENCY_MODE
