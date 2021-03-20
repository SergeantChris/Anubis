import requests
import sys
import os
import random
import time

# Client is executed locally
localhost = 'http://127.0.0.1'
NETIFACE = 'lo'	 # this should be eth0 or em0 in order for the vms to work
# TODO: define way to get parameters from command line (or file?)

def cli_insert(port, param):
    response = requests.post(localhost + ':' + port + '/user/insert', param)
    return response.text

def cli_delete(port, param):
    response = requests.post(localhost + ':' + port + '/user/delete', param)
    return response.text

def cli_query(port, param):
    response = requests.post(localhost + ':' + port + '/user/query', param)
    return response.text

if __name__ == '__main__':

    # list of all ports
    ports = ['5000', '5001', '5002']
    # list of all ips
    ips = [localhost]

    # test 1
    f = open("insert.txt", "r")
    inserts = f.read()
    inserts = inserts.splitlines()
    print("Insert requests testing...")
    now = time.time()
    for insert in inserts:
        insert_list = insert.split(", ")
        song_deats = {"key": insert_list[0],
                      "value": insert_list[1]}
        # randomly choose ip and port for insert
        port = random.choice(ports)
        _ = cli_insert(port, song_deats)

    later = time.time()
    difference = later - now
    print("The throughput is ", difference)
    f.close()

    # test 2
    f = open("query.txt", "r")
    queries = f.read()
    queries = queries.splitlines()
    print("Query requests testing...")
    now = time.time()
    for query in queries:
        song_deats = {"song_name": query}
        # randomly choose ip and port for insert
        port = random.choice(ports)
        _ = cli_query(port, song_deats)
    later = time.time()
    difference = later - now
    print("The throughput is ", difference)
    f.close()
    exit(0)

    # # test 3
    # if len(sys.argv) == 2 and sys.argv[1] in ('-l'):
    #     f = open("requests.txt", "r")
    #     requests = f.read()
    #     requests = requests.splitlines()
    #     for request in requests:
    #         request_list = request.split(", ")
    #         if request_list[0] == "insert":
    #             song_deats = {"key": request_list[1],
    #                           "value": request_list[2]}
    #             # randomly choose ip and port for insert
    #             port = random.choice(ports)
    #             print(cli_insert(port, song_deats))
    #         else:
    #             song_deats = {"song_name": request_list[1]}
    #             # randomly choose ip and port for insert
    #             port = random.choice(ports)
    #             print(cli_query(port, song_deats))
