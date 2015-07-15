# Mono PAC

A PAC(Proxy auto-config) file generator working with fetched China IP range, which helps walk around GFW.

Mono generates a much smaller and faster PAC file than any other project does.

The PAC file is designed to be hosted on your openwrt routers for your mobile device, which means the size and the efficiency have the highest priority. When it's hosted on your VPS with gzip or used on your computer, we don't care that things.

The minimal unit of the APNIC's IP allocation is 256, which means it's safe to do `IP >> 8` on IP range data. If you use data from some otherthings, modify my codes first.

## Installation

```
$ git clone https://github.com/blackgear/mono_pac.git
```

## Usage

```
$ python ./src/make.py -h
usage: MonoPac [-h] [-b blackList] [-w whiteList] [-i ipList] -p proxyList
               [-o pacFile]

Mono Pac Generator

optional arguments:
  -h, --help    show this help message and exit
  -b blackList  Path of the black list
  -w whiteList  Path of the white list
  -i ipList     Path of the iprange list
  -p proxyList  Proxy parameter in the pac file
  -o pacFile    Path of the output pac file

Across the Great Firewall, we can reach every corner in the world.

$ python ./src/make.py -p "SOCKS5 192.168.1.1:1080;SOCKS 192.168.1.1:1080" -o ./proxy.pac
```
Both Python 2 and 3 are supported.

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
  Direct <----|If domain in blackList |  |
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
  Direct <----|    If IP in ipList    |
              +-----------------------+
                          |
                          v False
                        Proxy
```

When you browse http://127.0.0.1/index.html, The `Host` will be `127.0.0.1`, `0.0.1`, `0.1`, `1`. Then `dnsResolve` will return `127.0.0.1`.

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
Performance with Node.js:
```
$ ./performance_test.sh
Testing pac generated by blackgear/mono_pac
avg: 2.268us

Testing pac generated by breakwa11/gfw_whitelist
avg: 4.331us

Testing pac generated by Leask/flora_pac
avg: 145.960us

Testing pac generated by Leask/flora_pac-mod
avg: 4.781us

Testing pac generated by usufu/flora_pac
avg: 2.939us

-rw-r--r--  1 Daniel  staff   45662  2 24 21:53 blackgear-mono_pac.pac
-rw-r--r--  1 Daniel  staff  165129  2 24 21:53 Leask-Flora_Pac-mod.pac
-rw-r--r--  1 Daniel  staff   74738  2 24 21:53 Leask-Flora_Pac.pac
-rw-r--r--  1 Daniel  staff   92854  2 24 21:53 breakwa11-gfw_whitelist.pac
-rw-r--r--  1 Daniel  staff  254539  2 24 21:53 usufu-Flora_Pac.pac
```

Performance with Safari:
```
Testing pac generated by blackgear/mono_pac
Average 192.78ms in 100,000 tests

Testing pac generated by breakwa11/gfw_whitelist
Average 463.54ms in 100,000 tests

Testing pac generated by Leask/flora_pac
Average 4934.83ms in 100,000 tests

Testing pac generated by Leask/flora_pac-mod
Average 400.81ms in 100,000 tests

Testing pac generated by usufu/flora_pac
Average 281.89ms in 100,000 tests
```

MonoPac is the smallest one with a full ipList. It's even smaller than Flora_Pac with a minimal ipList.

Leask-Flora_Pac.pac use a minimal ipList ignored the last two bytes of every ip, while others use a full ipList.

MonoPac is the fastest one with full functions. It's even faster than gfw_whitelist with a minimal functions.

breakwa11-gfw_whitelist.pac does not check if domain in white or black list. while others use the same O(1) algorithm to check the domains white or black list.

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
