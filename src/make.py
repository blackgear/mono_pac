#!/usr/bin/env python
# -*- coding: utf-8 -*-

def loadProxy(data):
    lines = data.splitlines()
    return '"{}"'.format(';'.join(lines))

def loadRange(data):
    lines = data.splitlines()

    codelist = [[] for i in range(256)]
    masklist = [[] for i in range(256)]

    for line in lines:
            item = line.split('/')
            atom = item[0].split('.')
            codelist[int(atom[0])].append(int(atom[1]) << 8 | int(atom[2]) << 0)
            masklist[int(atom[0])].append(24 - int(item[1]))

    codelist = ['[{}]'.format(','.join(map(str, x))) for x in codelist]
    masklist = ['[{}]'.format(','.join(map(str, x))) for x in masklist]

    codelist = '[{}]'.format(','.join(codelist).replace('[]','0'))
    masklist = '[{}]'.format(','.join(masklist).replace('[]','0'))

    return codelist, masklist


def loadDomain(data):
    lines = filter(lambda x:not x.startswith('#') and x, data.splitlines())
    domains = []
    for line in lines:
        if sum(map(lambda x:line.endswith(x), lines)) == 1:
            domains.append(line)
    return '{{{}}}'.format(','.join(map(lambda x:'"{}":1'.format(x), domains)))

def main():
    with open('mono.js') as f:
        payload = f.read()

    with open('proxyList') as f:
        proxylist = loadProxy(f.read())

    with open('whiteList') as f:
        whitelist = loadDomain(f.read())

    with open('blackList') as f:
        blacklist = loadDomain(f.read())

    with open('ipList') as f:
        codelist, masklist = loadRange(f.read())

    payload = payload.replace('__proxyList__', proxylist)
    payload = payload.replace('__whiteList__', whitelist)
    payload = payload.replace('__blackList__', blacklist)
    payload = payload.replace('__codeList__', codelist)
    payload = payload.replace('__maskList__', masklist)

    print(payload)

if __name__ == '__main__':
    main()
