import requests
import sys
import os
from pprint import pprint

# Client is executed locally
LOCAL_MODE = False
if LOCAL_MODE:
    NETIFACE = 'lo'

else:
    NETIFACE = 'ens3'

HTTP = 'http://'

def cli_insert(port, param, ip):
    response = requests.post(HTTP + ip + ':' + port + '/user/insert', param)
    return response.text

def cli_delete(port, param, ip):
    response = requests.post(HTTP + ip + ':' + port + '/user/delete', param)
    return response.text

def cli_query(port, param, ip):
    response = requests.post(HTTP + ip + ':' + port + '/user/query', param)
    return response.text

def cli_depart(port, ip):
    response = requests.post(HTTP + ip + ':' + port + '/user/depart', {})
    return response.text

def cli_overlay(port, ip):
    response = requests.post(HTTP + ip + ':' + port + '/user/overlay', {})
    return eval(response.text)


if __name__ == '__main__':

    # get the port from the command line
    if len(sys.argv) < 3 or sys.argv[1] not in ('-p', '-P'):
        print('Tell me the port, e.g. -p 5000')
        exit(0)

    port = sys.argv[2]
    ip = os.popen('ip addr show ' + NETIFACE +
                  ' | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\''
                  ).read().strip()

    while 1:
        action = input('Tell us the action. To exit the cli write exit or Ctrl+C.\n')

        if action == 'depart':
            print(cli_depart(port, ip))
            exit(0)

        elif action == 'overlay':
            pprint(cli_overlay(port, ip))

        elif action[:7] == 'insert,':
            insert_list = action.split(", ")
            print('insert list:')
            pprint(insert_list)
            song_deats = {"key": insert_list[1],
                          "value": insert_list[2]}
            print(cli_insert(port, song_deats, ip))

        elif action[:6] == 'query,':
            query_list = action.split(", ")
            song_name = query_list[1]
            req = {
                "song_name": song_name
            }
            print(cli_query(port, req, ip))

        elif action[:7] == 'delete,':
            delete_list = action.split(", ")
            song_deats = {"key": delete_list[1]}
            print(cli_delete(port, song_deats, ip))

        elif action == 'exit':
            exit(0)

        elif action == 'help':
            print("\nWrite overlay in order to print the overlay of the chord network")
            print("Write depart to depart this node from the network")
            print("Write insert, <name of the song>, <value> to add a song in the network")
            print("Write query, <name of the song> to find and get a song from the network")
            print("Write delete, <name of the song>, to delete a song from the network\n")

        else:
            print('Invalid input. Try help!')
