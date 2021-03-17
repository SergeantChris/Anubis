import requests
import sys
import os
import random
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

    ports = ['5000', '5001', '5002']
    ips = [localhost]
    f = open("insert.txt", "r")
    inserts = f.read()
    inserts = inserts.splitlines()
    for insert in inserts:
        insert_list = insert.split(", ")
        song_deats = {"key": insert_list[0],
                      "value": insert_list[1]}
        port = random.choice(ports)
        cli_insert(port, song_deats)
        print(".", end ="")
    print()
