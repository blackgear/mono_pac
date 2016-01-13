#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://its.pku.edu.cn/oper/liebiao.jsp

with open('pkulist') as f:
    data = f.read()

for line in filter(lambda x: '.' in x, data.splitlines()):
    item = line.split(' ')
    print('{}/{}'.format(item[0], sum([bin(int(x)).count('1') for x in item[-1].split('.')])))
