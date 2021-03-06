import requests

# Client is executed locally
url = 'http://127.0.0.1:5000'

# TODO: define way to get parameters from command line (or file?)

def cli_insert(param):
    # construct the right json object and call the endpoint
    call_params = {}
    requests.post(url + '/user/insert', call_params)

def cli_delete(param):
    # construct the right json object and call the endpoint
    call_params = {}
    requests.post(url + '/user/delete', call_params)

def cli_query(param):
    # construct the right json object and call the endpoint
    call_params = {}
    requests.post(url + '/user/query', call_params)

def cli_depart(param):
    # construct the right json object and call the endpoint
    call_params = {}
    requests.post(url + '/user/depart', call_params)

def cli_overlay(param):
    # construct the right json object and call the endpoint
    call_params = {}
    requests.post(url + '/user/overlay', call_params)