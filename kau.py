#!/bin/env python
import requests
import ast

HOST       = 'http://10.149.52.2:8080'
ADMIN_USER = 'admin'
ADMIN_PASS = 'changeme'
REALM      = 'master'
ATTRIBUTES = {
    'testattr': 'testattrvalue'
}

class RestKey:
    token = ''
    base_url = ''
    auth_header = {}

    def __init__(self, host: str, user: str, password: str):
        self.base_url = f'{host}/auth'
        self.token = self._get_token(user, password)
        self.auth_header = {
            'content-type': 'application/json',
            'Authorization' : 'Bearer '+ self.token
        }


    def _get_token(self, user, password):
        url = f'{self.base_url}/realms/master/protocol/openid-connect/token'
        params = {
            'client_id': 'admin-cli',
            'grant_type': 'password',
            'username' : user,
            'password': password
        }
        x = requests.post(url, params, verify=False).content.decode('utf-8')
        return str(ast.literal_eval(x)['access_token'])


    def create_user(self, realm: str, name: str, enabled: bool = False):
        url = f'{self.base_url}/admin/realms/{realm}/users'
        params = {
            'username': name,
            'enabled': enabled
        }
        request = requests.post(url, headers=self.auth_header, json=params)
        print(f'Create User - Status Code: ({request.status_code})')


    def get_users(self, realm: str, limit: int = -1):
        url = f'{self.base_url}/admin/realms/{realm}/users?max={limit}'
        request = requests.get(url, headers=self.auth_header)
        return request.json()


    def add_attr(self, realm: str, user: dict, new_attr: dict, verbose: bool = True):
        user_id = user['id']
        url = f'{self.base_url}/admin/realms/{realm}/users/{user_id}'

        try:
            old_attr = user['attributes']
        except KeyError:
            old_attr = None

        if old_attr:
            attributes = old_attr.copy()
            attributes.update(new_attr)
        else:
            attributes = new_attr

        params = {
            'attributes': attributes
        }

        response = requests.put(url, headers=self.auth_header, json=params)
        if verbose:
            print(f'{user_id} status_code {response.status_code}')



if __name__ == '__main__':
    r = RestKey(HOST, ADMIN_USER, ADMIN_PASS)
    users = r.get_users(REALM)
    i = 0
    for u in users:
        r.add_attr(REALM, u, ATTRIBUTES)
        i+=1
    print(f'Finished updating {i} users.')

