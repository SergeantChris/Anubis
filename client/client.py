import requests
import sys
import os
from pprint import pprint
import hashlib

# Client is executed locally
localhost = 'http://127.0.0.1'
NETIFACE = 'lo'	 # this should be eth0 or em0 in order for the vms to work
# TODO: define way to get parameters from command line (or file?)

def hash(key):
    return hashlib.sha1(key.encode('utf-8')).hexdigest()

def cli_insert(port, param):
    response = requests.post(localhost + ':' + port + '/user/insert', param)
    return response.text

def cli_delete(port, param):
    response = requests.post(localhost + ':' + port + '/user/delete', param)
    return response.text

def cli_query(port, param):
    response = requests.post(localhost + ':' + port + '/user/query', param)
    return response.text

def cli_depart(port):
    response = requests.post(localhost + ':' + port + '/user/depart', {})
    return response.text

def cli_overlay(port):
    response = requests.post(localhost + ':' + port + '/user/overlay', {})
    return eval(response.text)


if __name__ == '__main__':

    # get the port from the command line
    if len(sys.argv) < 3 or sys.argv[1] not in ('-p', '-P'):
        print('Tell me the port, e.g. -p 5000')
        exit(0)

    port = sys.argv[2]

    while 1:
        action = input('Tell us the action. To exit the cli write exit or Ctrl+C.\n')

        if action == 'depart':
            print(cli_depart(port))
            exit(0)

        elif action == 'overlay':
            pprint(cli_overlay(port))

        elif action[:7] == 'insert,':
            insert_list = action.split(", ")
            print('insert list:')
            pprint(insert_list)
            song_deats = {"key": insert_list[1],
                          "value": insert_list[2]}
            print(cli_insert(port, song_deats))

        elif action[:6] == 'query,':
            query_list = action.split(", ")
            song_name = query_list[1]
            req = {
                "song_name": song_name
            }
            print(cli_query(port, req))

        elif action[:7] == 'delete,':
            delete_list = action.split(", ")
            song_deats = {"key": delete_list[1]}
            print(cli_delete(port, song_deats))

        elif action == 'exit':
            exit(0)

        else:
            print('Invalid input. Try help!')
