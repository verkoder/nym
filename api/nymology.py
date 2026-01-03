#!/usr/bin/env python
# encoding: utf-8
'''
nymology.py -- Nymology API Python wrapper
'''
import json
import requests

DATASETS = (
    'fable',
    'fortune',
    'phrase',
    'polynym',
    'polymap',
    'polyset',
    'quadranym',
    'quadraset',
    'queue',
    'quote',
    'story',
    'tale',
    'storyline',
    'taleline',
    'vectornym',
    'winner'
)

def get_request(url):
    'process GET request'
    response = requests.get(url)
    if response.status_code != 200:
        return f'Error {response.status_code} -- {response.text}'
    return response.json()

class NymologyAPI:
    home = 'api/data'
    url = 'http://nymology.org/api/'
    def __init__(self, local=None, home=None, username=None, password=None):
        if local is not None:
            self.url = 'http://127.0.0.1:8000/api/'
        if home is not None:
            self.home = home
        if username is not None and password is not None:
            self.auth = (username, password)

    def create(self, dataset, data):
        'create dataset item from dictionary (POST request)'
        data['user'] = self.auth[0]
        response = requests.post(f'{self.url}{dataset}/', auth=self.auth, data=data)
        if response.status_code != 201:
            return f'Error {response.status_code} -- {response.text}'
        return response.json()

    def read(self, dataset, pk):
        'read dataset item by primary key (GET request)'
        return get_request(f'{self.url}{dataset}/{pk}/')

    def update(self, dataset, pk, data):
        'update dataset item pk from dictionary (PUT request)'
        response = requests.put(f'{self.url}{dataset}/{pk}/', auth=self.auth, data=data)
        if response.status_code != 200:
            return f'Error {response.status_code} -- {response.text}'
        return response.json()

    def delete(self, dataset, pk):
        'delete dataset item by primary key (DELETE request)'
        response = requests.delete(f'{self.url}{dataset}/{pk}/', auth=self.auth)
        if response.status_code != 204:
            return f'Error {response.status_code} -- {response.text}'
        return 'DELETED!'

    def get_page(self, dataset, page=None):
        'download dataset page, first page if not given (GET request)'
        return get_request(f'{self.url}{dataset}/{"" if page is None else "?page="+str(page)}')

    def get_choices(self, dataset):
        'pk/name of dataset (GET requests)'
        data = []
        page = 0
        while 1:
            page += 1
            batch = self.get_page(f'{dataset}-id', page)
            data.extend([(x[f'{dataset}_id'], x['name']) for x in batch['results']])
            if not batch['next']:
                break
        return data

    def get_data(self, dataset):
        'download entire dataset (GET requests)'
        print(f'Loading {dataset} data..')
        data = []
        page = 0
        while 1:
            page += 1
            batch = self.get_page(dataset, page)
            data.extend(batch['results'])
            if not batch['next']:
                break
        print(f'{len(data)} {dataset.title()} objects loaded!')
        return data

    def get_file(self, dataset):
        'load dataset from file (JSON)'
        with open(f'{self.home}/{dataset}.json', 'r') as f:
            data = json.load(f)
            print(f'{len(data)} {dataset.title()} objects loaded!')
            return data

    def save_file(self, dataset):
        'download/save dataset to file (GET requests -> JSON)'
        data = self.get_data(dataset)
        with open(f'{self.home}/{dataset}.json', 'w') as f:
            json.dump(data, f)
        print(f'{len(data)} {dataset.upper()} objects saved!\n')

    def save_database(self):
        'download/save db; file per dataset (GET requests >> JSON)'
        for dataset in DATASETS:
            self.save_file(dataset)

    def endpoints(self):
        'list all endpoints (GET request)'
        return get_request(self.url)
