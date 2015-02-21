# Mono PAC

A PAC(Proxy auto-config) file generator with fetched China IP range, which helps walk around GFW.

Mono generates a much smaller PAC file than any other project does.

## Installation
<pre>
$ git clone https://github.com/BlackGear/Mono_PAC.git
</pre>

## Uasge
Edit config file in ./src, then:
<pre>
$ python ./src/make.py
</pre>
Both Python 2 and 3 are supported.

## Configuration
- WhiteList / BlackList:

One domains per line, # for comments. Domains will be automatic merged when generating. So you can just add domains to the list.

- ipList:

One record per line with IP/CIDR format.

Records MUST be manually sort and unique before using.

- proxyList:

Proxy config infomations in order.
<pre>
PROXY host:port   = use HTTP proxy
SOCKS5 host:port  = use Socks5 proxy
DIRECT            = Do not use proxy
</pre>

Note: Safari do not understand "SOCKS5", use "SOCKS" instead, you can also use a more compatible form like:
<pre>
SOCKS5 xxxx:xxxx
SOCKS xxxx:xxxx
DIRECT
</pre>

## To do
- Unique, merge, sort ipList before generate.
