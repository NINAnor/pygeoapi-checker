#!/usr/bin/env python3

import click
import requests
import json
import logging


logging.basicConfig(level=logging.INFO)

REQUESTS = {}

IGNORE_FIELD = [
    'geometry',
    'features',
]

def find_links(obj, url):
    result = []
    if isinstance(obj, list):
        result = list(filter(lambda x:x, [find_links(e, url) for e in obj]))
    elif isinstance(obj, dict):
        if not (obj.get('rel') and obj.get('rel') in ['alternate', 'next', 'self', 'collection']):
            result = list(filter(lambda x:x,[find_links(e, url) for k, e in obj.items() if k not in IGNORE_FIELD]))
    else:
        if isinstance(obj, str) and obj.startswith(url):
            result.append([obj])

    return set([item for row in result for item in row])

IGNORE_FORMATS = [
    'f=jsonld',
    'f=html',
]

def make_request(url, base = None):
    if url in REQUESTS or any([url.endswith(suffix) for suffix in IGNORE_FORMATS]):
        return

    try:
        logging.info(url)
        response = requests.get(url)
        body = response.json()
        REQUESTS[url] = response.status_code
        links = find_links(body, base or url)

        for link in links:
            make_request(link, base=base)
    except Exception as exc:
        logging.error(url)
        REQUESTS[url] = str(exc)


@click.command()
@click.argument('url')
@click.option('--output', default='result.json')
def recursive_check_url(url, output):
    make_request(url)

    groups = {}
    for k, v in REQUESTS.items():
        groups[v] = groups.get(v, []) + [k]

    with open(output, "w") as f:
        json.dump(groups, f, indent=4)


if __name__ == '__main__':
    recursive_check_url()
