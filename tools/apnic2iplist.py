#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('delegated-apnic-latest') as f:
    data = f.read()

lines = data.splitlines()

codelist = [[] for i in range(256)]
masklist = [[] for i in range(256)]

for line in filter(lambda x:x.startswith('apnic|CN|ipv4'),lines):
        item = line.split('|')
        print('{}/{}'.format(item[3], 33 - int(item[4]).bit_length()))
