import requests
import sys
from pprint import pprint

# Client is executed locally
localhost = 'http://127.0.0.1'

# TODO: define way to get parameters from command line (or file?)


def cli_insert(port, param):
    call_params = {}
    requests.post(localhost + '/user/insert', call_params)

def cli_delete(port, param):
    call_params = {}
    requests.post(localhost + '/user/delete', call_params)

def cli_query(port, param):
    call_params = {}
    requests.post(localhost + '/user/query', call_params)

def cli_depart(port):
    response = requests.post(localhost + ':' + port + '/user/depart', {})
    return response.text

def cli_overlay(port):
    response = requests.post(localhost + ':' + port + '/user/overlay', {})
    return eval(response.text)


if __name__ == '__main__':

    # get the port from the command line
    if len(sys.argv) < 4 or sys.argv[1] not in ('-p', '-P') or sys.argv[3] not in ('depart', 'overlay'):
        print('Tell me the port, e.g. -p 5000')
        exit(0)

    port = sys.argv[2]
    action = sys.argv[3]

    if action == 'depart':
        print(cli_depart(port))

    if action == 'overlay':
        pprint(cli_overlay(port))
    
    exit(0)
