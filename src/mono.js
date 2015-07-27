/*
 * Copyright (C) 2015 BlackGear
 * https://github.com/BlackGear/Mono_PAC
 */
function merge(obj, key) {
    obj[key] = 1;
    return obj;
}

var tunnel = __proxyList__;
var direct = "DIRECT";
var whiteList = "__whiteList__".split("|").reduce(merge, {});
var blackList = "__blackList__".split("|").reduce(merge, {});
var codeList = __codeList__;
var maskList = __maskList__;

function FindProxyForURL(url, host) {
    if (isPlainHostName(host)) {
        return direct;
    }

    var domain = host;
    var pos = 0;

    do {
        if (blackList.hasOwnProperty(domain)) {
            return tunnel;
        }
        if (whiteList.hasOwnProperty(domain)) {
            return direct;
        }
        pos = host.indexOf(".", pos) + 1;
        domain = host.substring(pos);
    } while (pos > 0);

    var IP = dnsResolve(host);

    if (!IP) {
        return tunnel;
    }

    if (IP.indexOf(":") >= 0) {
        return direct;
    }

    var atom = IP.split(".");
    var code = ((atom[1] & 0xff) << 8) | ((atom[2] & 0xff));
    var hash = atom[0];

    var codeLine = codeList[hash];
    var maskLine = maskList[hash];

    if (codeLine === "") {
        return tunnel;
    }

    if (maskLine === "10") {
        return direct;
    }

    var min = 0;
    var max = codeLine.length;
    var mid = max >> 1;

    do {
        if (codeLine[mid].charCodeAt(0) > code) {
            max = mid;
        } else {
            min = mid;
        }
        mid = (min + max) >> 1;
    } while (min + 1 < max);

    if (code - codeLine[min].charCodeAt(0) >> parseInt(maskLine[min], 16) === 0) {
        return direct;
    }

    return tunnel;
}
