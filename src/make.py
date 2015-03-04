#!/usr/bin/env python
# -*- coding: utf-8 -*-

class DomainTree(object):
    def __init__(self, name=''):
        self.name = name
        self.node = {}
        self.mark = False
        self.list = []

    def insert(self, domain):
        domains = domain.rsplit('.', 1)
        node = self.node.setdefault(domains[-1], DomainTree(domains[-1]))
        if len(domains) == 1:
            node.mark = True
        else:
            node.insert(domains[0])

    def reduce(self, suffix=''):
        suffix = self.name + '.' + suffix if suffix else self.name
        if self.mark is True:
            self.list = [suffix]
        else:
            self.list = []
            for name in self.node:
                self.node[name].reduce(suffix)
                self.list.extend(self.node[name].list)

class RouteChain(object):
    def __init__(self):
        self.line = []
        self.list = []

    def insert(self, ipnet):
        addr, mask = ipnet.split('/')
        bits = addr.split('.')
        addr = 0
        for byte in bits:
            addr = (addr << 8) + int(byte)
        mask = 1 << 32 - int(mask)
        self.line.append((addr,mask))

    def reduce(self):
        self.line.sort(key=lambda x: x[0])
        head = 0
        line = []
        for (addr, mask) in self.line:
            flag = addr + mask
            if head > flag:
                continue
            if head > addr:
                addr, _ = line.pop()
                mask = flag - addr
            head = flag
            line.append((addr, mask))
        for (addr, mask) in line:
            while mask > 0:
                head = 1 << mask.bit_length() - 1
                if addr + head >> 24 != addr >> 24:
                    head = (((addr >> 24) + 1) << 24) - addr
                self.list.append((addr, head))
                mask = mask - head
                addr = addr + head

def load_config(data):
    lines = []
    for line in data.splitlines():
        lines.append(line.split('#')[0].strip())
    return filter(None, lines)

def load_proxy(data):
    return '"{};"'.format(';'.join(load_config(data)))

def load_range(data):
    lines = load_config(data)
    lines.append('0.0.0.0/8')
    lines.append('10.0.0.0/8')
    lines.append('127.0.0.0/8')
    lines.append('169.254.0.0/16')
    lines.append('172.16.0.0/12')
    lines.append('192.0.0.0/24')
    lines.append('192.0.2.0/24')
    lines.append('192.88.99.0/24')
    lines.append('192.168.0.0/16')
    lines.append('198.18.0.0/15')
    lines.append('198.51.100.0/24')
    lines.append('203.0.113.0/24')
    lines.append('224.0.0.0/4')
    lines.append('240.0.0.0/4')

    route = RouteChain()
    for line in lines:
        route.insert(line)
    route.reduce()

    codelist = [[] for _ in range(256)]
    masklist = [[] for _ in range(256)]

    for (addr, mask) in route.list:
        atom = addr >> 24
        codelist[atom].append(addr >> 8 & 0x00FFFF)
        masklist[atom].append(mask.bit_length()-9)

    codelist = ['[{}]'.format(','.join(map(str, x))) for x in codelist]
    masklist = ['[{}]'.format(','.join(map(str, x))) for x in masklist]

    codelist = '[{}]'.format(','.join(codelist).replace('[]','0'))
    masklist = '[{}]'.format(','.join(masklist).replace('[]','0'))

    return codelist, masklist

def load_domain(data):
    lines = load_config(data)
    domains = DomainTree()
    for line in lines:
        domains.insert(line)
    domains.reduce()
    return '{{{}}}'.format(','.join(map('"{}":1'.format, domains.list)))

def main():
    with open('mono.min.js') as f:
        payload = f.read()

    with open('proxyList') as f:
        proxylist = load_proxy(f.read())

    with open('whiteList') as f:
        whitelist = load_domain(f.read())

    with open('blackList') as f:
        blacklist = load_domain(f.read())

    with open('ipList') as f:
        codelist, masklist = load_range(f.read())

    payload = payload.replace('__proxyList__', proxylist)
    payload = payload.replace('__whiteList__', whitelist)
    payload = payload.replace('__blackList__', blacklist)
    payload = payload.replace('__codeList__', codelist)
    payload = payload.replace('__maskList__', masklist)

    print(payload)

if __name__ == '__main__':
    main()
