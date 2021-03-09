import requests
import sys

# Client is executed locally
localhost = 'http://127.0.0.1'

# TODO: define way to get parameters from command line (or file?)


def cli_insert(param):
    call_params = {}
    requests.post(localhost + '/user/insert', call_params)

def cli_delete(param):
    call_params = {}
    requests.post(localhost + '/user/delete', call_params)

def cli_query(param):
    call_params = {}
    requests.post(localhost + '/user/query', call_params)

def cli_depart(port):
    requests.post(localhost + ':' + port + '/user/depart', {})

def cli_overlay(port):
    response = requests.post(localhost + ':' + port + '/user/overlay', {})
    return response.text


if __name__ == '__main__':

    # get the port from the command line
    if len(sys.argv) < 3 or sys.argv[1] not in ('-p', '-P'):
        print('Tell me the port, e.g. -p 5000')
        exit(0)

    port = sys.argv[2]

    # test call for depart
    cli_depart(port)
    # test call for overlay
    #print(cli_overlay(port))
