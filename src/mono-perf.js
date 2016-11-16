/*
 * Copyright (C) 2015 BlackGear
 * https://github.com/BlackGear/Mono_PAC
 */
var tunnel = __proxyList__;
var direct = "DIRECT";
var whiteList = __whiteList__;
var blackList = __blackList__;
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

    if (codeLine === 0) {
        return tunnel;
    }

    if (maskLine === 16) {
        return direct;
    }

    var min = 0;
    var max = codeLine.length;
    var mid = max >> 1;

    do {
        if (codeLine[mid] > code) {
            max = mid;
        } else {
            min = mid;
        }
        mid = (min + max) >> 1;
    } while (min + 1 < max);


    if (code - codeLine[min] >> maskLine[min] === 0) {
        return direct;
    }

    return tunnel;
}
