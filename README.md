# Mono PAC

A PAC(Proxy auto-config) file generator working with fetched China IP range, which helps walk around GFW.

Mono generates a much smaller and faster PAC file than any other project does.

This PAC file is designed to be hosted on your Openwrt routers for your mobile device, which means the size and the efficiency have the highest priority. When it's hosted on your VPS with gzip or used on your computer, we don't care that things.

The minimal unit of the APNIC's IP allocation is 256, which means it's safe to do `IP >> 8` on IP range data. If you use data from some otherthings, modify my codes first.

## Installation

```
$ git clone https://github.com/blackgear/mono_pac.git
```

## Usage

```
$ cd ./src
$ python ./make.py -h
usage: MonoPac [-h] [-b blackList] [-w whiteList] [-i ipList] -p proxyList
               [-m] [-o pacFile]

Mono Pac Generator

optional arguments:
  -h, --help    show this help message and exit
  -b blackList  Path of the black list
  -w whiteList  Path of the white list
  -i ipList     Path of the iprange list
  -p proxyList  Proxy parameter in the pac file
  -m            Use unicode compression
  -o pacFile    Path of the output pac file

Across the Great Firewall, we can reach every corner in the world.

$ python ./make.py -p "SOCKS5 192.168.1.1:1080;SOCKS 192.168.1.1:1080" -o ./proxy.pac
```

**ONLY** Python 2 is supported.

`-m` option reduce 45% file size with 2.8% extra efficiency loss, but it may cause some PAC management extensions like SwitchOmega crash.

## Details

When you browse https://www.google.com/abc, The Pac works in this way:

```
              +-----------------------+
              |      Grab Host:       |
              |  Host=www.google.com  |
              +-----------------------+
                          |
                          v
              +-----------------------+
              | Domain=www.google.com |
              | Domain=google.com     |<-+
              | Domain=com            |  |
              +-----------------------+  |
                          |              |
                          v              |
         True +-----------------------+  |
   Proxy <----|If domain in blackList |  |
              +-----------------------+  |
                          |              |
                          v False        |
         True +-----------------------+  |
  Direct <----|If domain in whiteList |  |
              +-----------------------+  |
                          |              |
                          v False        |
              +-----------------------+  |
              |    If . in domain     |--+
              +-----------------------+
                          |
                          v False
              +-----------------------+
              |      Dns resolve      |
              +-----------------------+
                          |
                          v
         True +-----------------------+
  Proxy  <----|      If IP = nil      |
              +-----------------------+
                          |
                          v False
         True +-----------------------+
  Direct <----|   If IP = IPv6 addr   |
              +-----------------------+
                          |
                          v False
         True +-----------------------+
  Direct <----|    If IP in ipList    |
              +-----------------------+
                          |
                          v False
                        Proxy
```

When you browse http://127.0.0.1/index.html, The `Domain` will be `127.0.0.1`, `0.0.1`, `0.1`, `1`. Then `dnsResolve` will return `127.0.0.1`.

`dnsResolve` return IPv4 only in IE and Chromium, `dnsResolve` can return IPv6 in Firefox.

IE via http://blogs.msdn.com/b/wndp/archive/2006/07/18/ipv6-wpad-for-winhttp-and-wininet.aspx

Chromium via https://code.google.com/p/chromium/issues/detail?id=24641

Firefox via https://github.com/blackgear/mono_pac/pull/2

## Configs

All config files can use '#' as comments, all things behind '#' is ignored, space is automatic striped.

Config files like this is acceptable:

```
# Twitter
twitter.com
t.co
tweetdeck.com
twimg.com        # This domain is used for images
```

It will be prased as

```
twitter.com
t.co
tweetdeck.com
twimg.com
```

### blackList:

One domains per line.

### whiteList:

One domains per line.

### ipList:

One record per line with IP/CIDR or IP/Wildcard format.

Both `100.100.100.0/24` and `100.100.100.0/255.255.255.0` are acceptable.

### proxyList:

Proxy Configs separated by ";".

Available proxy configs:
```
PROXY host:port   = use HTTP proxy
SOCKS5 host:port  = use Socks5 proxy
DIRECT            = Do not use proxy
```

Example: `PROXY 127.0.0.1:8080;DIRECT`

Note: The latter config is the fallback of the former one. There is no limit on the length of the fallback list.

Note: Safari don't accept `SOCKS5`, use `SOCKS` instead, you can also use a more compatible form like: `SOCKS5 host:port;SOCKS host:port`, Safari will ignore the first config and use the second one.

Note: The `DIRECT` in the end have a potential risk cause the dns pollution affecting blackList domains.

Note: When you use socks proxy, whether dns resolve will through the proxy is determined by the Apps itself. When you use http proxy, the dns resolve will always through the proxy.

## Performance
Test with Node.js:
```
$ node test.js
Testing pac generated by blackgear-mono_pac.pac
avg: 5.984us
Testing pac generated by blackgear-mono_pac-unicode.pac
avg: 6.152us
Testing pac generated by Leask-Flora_Pac-mod.pac
avg: 12.872us
Testing pac generated by usufu-Flora_Pac.pac
avg: 11.361us

$ ls -la *.pac
-rw-r--r--  1 Daniel  staff  165129 Feb 24 21:53 Leask-Flora_Pac-mod.pac
-rw-r--r--  1 Daniel  staff   16371 Jul 30 02:55 blackgear-mono_pac-unicode.pac
-rw-r--r--  1 Daniel  staff   29824 Jul 30 02:55 blackgear-mono_pac.pac
-rw-r--r--  1 Daniel  staff  254539 Feb 24 21:53 usufu-Flora_Pac.pac
```

MonoPac is the fastest and smallest PAC with full feature (blacklist, whitelist and full China IP range).

With the help of Unicode compress, the size become much smaller (30741 -> 17346).

## Trivia

The PAC instance will be reuse instead of start new instance for every request. The code in the root scope of the PAC file will be run only once. The code in the FindProxyForURL function's scope will be run each time you browser the internet.

Just test this two PAC files:

```
    var unixtime_ms = new Date().getTime();
    while(new Date().getTime() < unixtime_ms + 5000) {}
    function FindProxyForURL(url, host) {
        return "DIRECT;";
    }
```

```
    function FindProxyForURL(url, host) {
        var unixtime_ms = new Date().getTime();
        while(new Date().getTime() < unixtime_ms + 5000) {}
        return "DIRECT;";
    }
```

So put all definations in the root scope will accelerate the PAC file.

## LICENSE

The MIT License

Copyright (c) 2015 Daniel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
