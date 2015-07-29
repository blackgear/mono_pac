#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import sys

class DomainTree(object):
    def __init__(self, name=''):
        self.name = name
        self.node = {}
        self.head = False
        self.list = []

    def insert(self, domain):
        domains = domain.rsplit('.', 1)
        node = self.node.setdefault(domains[-1], DomainTree(domains[-1]))
        if len(domains) == 1:
            node.head = True
        else:
            node.insert(domains[0])

    def reduce(self, suffix=''):
        suffix = self.name + '.' + suffix if suffix else self.name
        if self.head is True:
            self.list = [suffix]
        else:
            self.list = []
            for name in self.node:
                self.node[name].reduce(suffix)
                self.list.extend(self.node[name].list)

class RouteChain(object):
    def __init__(self):
        self.list = []
        self.flag = True
        self.insert('0.0.0.0/8')
        self.insert('10.0.0.0/8')
        self.insert('127.0.0.0/8')
        self.insert('169.254.0.0/16')
        self.insert('172.16.0.0/12')
        self.insert('192.0.0.0/24')
        self.insert('192.0.2.0/24')
        self.insert('192.88.99.0/24')
        self.insert('192.168.0.0/16')
        self.insert('198.18.0.0/15')
        self.insert('198.51.100.0/24')
        self.insert('203.0.113.0/24')
        self.insert('224.0.0.0/4')
        self.insert('240.0.0.0/4')

    def __str__(self):
        self.reduce()
        line = []
        for (addr, mask) in self.list:
            line.append('{}.{}.{}.{}/{}'.format(
                (addr >> 24) % 256,
                (addr >> 16) % 256,
                (addr >>  8) % 256,
                (addr >>  0) % 256,
                (33 - mask.bit_length())))
        return '\n'.join(line)

    def __iter__(self):
        self.reduce()
        return iter(self.list)

    def insert(self, ipnet):
        self.flag = False
        addr, mask = ipnet.split('/')
        bits = addr.split('.')
        addr = 0
        for byte in bits:
            addr = (addr << 8) + int(byte)
        if '.' in mask:
            mask = sum([bin(int(x)).count('1') for x in mask.split('.')])
        mask = 1 << 32 - int(mask)
        self.list.append((addr, mask))

    def reduce(self):
        if self.flag:
            return
        self.list.sort(key=lambda x: x[0])
        head = -1
        rule = []
        for (addr, mask) in self.list:
            flag = addr + mask
            if head >= flag:
                continue
            if head >= addr:
                addr, _ = rule.pop()
                mask = flag - addr
            head = flag
            rule.append((addr, mask))
        self.list = []
        for (addr, mask) in rule:
            while mask > 0:
                head = 1 << mask.bit_length() - 1
                if addr + head >> 24 != addr >> 24:
                    head = (((addr >> 24) + 1) << 24) - addr
                self.list.append((addr, head))
                mask = mask - head
                addr = addr + head
        self.flag = True

def load_config(data):
    lines = []
    for line in data.splitlines():
        line = line.split('#')[0].strip()
        if line:
            lines.append(line)
    return lines

def load_integer_range(data):
    lines = load_config(data)
    route = RouteChain()
    for line in lines:
        route.insert(line)

    codelist = [[] for _ in range(256)]
    masklist = [[] for _ in range(256)]

    for (addr, mask) in route:
        atom = addr >> 24
        codelist[atom].append(addr >> 8 & 0x00FFFF)
        masklist[atom].append(mask.bit_length() - 9)

    codelist = json.dumps(codelist, separators=(',', ':')).replace('[]', '0')
    masklist = json.dumps(masklist, separators=(',', ':')).replace('[]', '0')

    return codelist, masklist

def load_unicode_range(data):
    lines = load_config(data)
    route = RouteChain()
    for line in lines:
        route.insert(line)

    codelist = ['' for _ in range(256)]
    masklist = ['' for _ in range(256)]

    for (addr, mask) in route:
        atom = addr >> 24
        codelist[atom] += unichr(addr >> 8 & 0x00FFFF)
        masklist[atom] += hex(mask.bit_length() - 9)[2:]

    templist = ''.join(codelist)
    splitcode = 0
    while unichr(splitcode) in templist:
        splitcode += 1
    codelist = unichr(splitcode).join(codelist)
    codelist = codelist.replace(u'\u000A', '\\n').replace(u'\u000D', '\\r')
    codelist = codelist.replace(u'\u2028', '\u2028').replace(u'\u2029', '\u2029')
    codelist = u'"{}".split("{}")'.format(codelist, unichr(splitcode))
    masklist = '.'.join(masklist)
    masklist = u'"{}".split(".")'.format(masklist)

    return codelist, masklist

def load_domain(data):
    lines = load_config(data)
    domains = DomainTree()
    for line in lines:
        domains.insert(line)
    domains.reduce()
    return '|'.join(domains.list)

def parse_args():
    parser = argparse.ArgumentParser(
        prog='MonoPac',
        description='Mono Pac Generator',
        epilog='Across the Great Firewall, we can reach every corner in the world.')

    parser.add_argument('-b', dest='blacklist', default='blackList', type=argparse.FileType('r'),
                        metavar='blackList', help='Path of the black list')
    parser.add_argument('-w', dest='whitelist', default='whiteList', type=argparse.FileType('r'),
                        metavar='whiteList', help='Path of the white list')
    parser.add_argument('-i', dest='iplist', default='ipList', type=argparse.FileType('r'),
                        metavar='ipList', help='Path of the iprange list')
    parser.add_argument('-p', dest='proxylist', required=True, metavar='proxyList',
                        help='Proxy parameter in the pac file')
    parser.add_argument('-m', dest='unicode', action='store_true',
                        help='Use unicode compression')
    parser.add_argument('-o', dest='output', default=sys.stdout, type=argparse.FileType('w'),
                        metavar='pacFile', help='Path of the output pac file')

    return parser.parse_args()

def main():
    args = parse_args()

    proxylist = '"{}"'.format(args.proxylist)
    whitelist = load_domain(args.whitelist.read())
    blacklist = load_domain(args.blacklist.read())
    if args.unicode == False:
        payload = open('mono.min.js').read()
        codelist, masklist = load_integer_range(args.iplist.read())
    else:
        payload = open('mono-unicode.min.js').read()
        codelist, masklist = load_unicode_range(args.iplist.read())

    payload = payload.replace('__proxyList__', proxylist)
    payload = payload.replace('__whiteList__', whitelist)
    payload = payload.replace('__blackList__', blacklist)
    payload = payload.replace('__codeList__', codelist)
    payload = payload.replace('__maskList__', masklist)

    args.output.write(payload.encode('utf-8'))

if __name__ == '__main__':
    main()
