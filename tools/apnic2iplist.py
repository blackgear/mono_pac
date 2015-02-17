#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('delegated-apnic-latest') as f:
    data = f.read()

lines = data.splitlines()
lines.append('apnic|CN|ipv4|127.0.0.0|256')
lines.append('apnic|CN|ipv4|192.168.0.0|65536')
lines.append('apnic|CN|ipv4|172.16.0.0|1048576')
lines.append('apnic|CN|ipv4|10.0.0.0|16777216')

codelist = [[] for i in range(256)]
masklist = [[] for i in range(256)]

for line in filter(lambda x:x.startswith('apnic|CN|ipv4'),lines):
        item = line.split('|')
        print('{}/{}'.format(item[3], 33 - int(item[4]).bit_length()))
