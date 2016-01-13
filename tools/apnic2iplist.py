#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://ftp.apnic.net/stats/apnic/delegated-apnic-latest

with open('delegated-apnic-latest') as f:
    data = f.read()

for line in filter(lambda x: x.startswith('apnic|CN|ipv4'), data.splitlines()):
    item = line.split('|')
    print('{}/{}'.format(item[3], 33 - int(item[4]).bit_length()))
