#!/usr/bin/env python3
import argparse
import json
import requests


""" Curl examples
curl 'https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/registry:pull'
curl -v https://index.docker.io/v2/library/registry/tags/list -i -H 'Authorization: Bearer {}'
"""


def get_token(auth_url, image_name, username, password):
    payload = {
        'service': 'registry.docker.io',
        'scope': 'repository:{image}:pull'.format(image=image_name)
    }

    if username is not None:
        auth = (username, password)    
    else:
        auth = ()
    r = requests.get(auth_url + '/token', params=payload, auth=auth)
    if not r.status_code == 200:
        print("Error status {}".format(r.status_code))
        raise Exception("Could not get auth token")

    j = r.json()
    return j['token']


def fetch_versions(index_url, token, image_name):
    h = {'Authorization': "Bearer {}".format(token)}
    r = requests.get('{}/v2/{}/tags/list'.format(index_url, image_name),
                     headers=h)
    return r.json()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('name', help='Name of image to list versions of such as alpine or curlimages/curl')
    p.add_argument('-t', '--token',
                   help='Auth token to use (automatically fetched if not specified)')
    p.add_argument('-i', '--index-url', default='https://index.docker.io')
    p.add_argument('-a', '--auth-url', default='https://auth.docker.io')
    p.add_argument('-u', '--username')
    p.add_argument('-p', '--password')

    args = p.parse_args()
    image_name = args.name if '/' in args.name else 'library/' + args.name
    token = args.token or get_token(auth_url=args.auth_url, image_name=image_name, 
                                    username=args.username, password=args.password)

    versions = fetch_versions(args.index_url, token, image_name)
    print(json.dumps(versions, indent=2))
