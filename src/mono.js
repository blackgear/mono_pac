function FindProxyForURL(url, host) {
    var tunnel = __proxyList__;
    var direct = "DIRECT;";

    if (isPlainHostName(host) || (host === "127.0.0.1") || (host === "localhost")) {
        return direct;
    };

    var whiteList = {__whiteList__};
    var blackList = {__blackList__};

    var suffix;
    var pos = host.lastIndexOf(".");

    while (pos > 0) {
        suffix = host.substring(pos + 1);
        if (whiteList.hasOwnProperty(suffix)) {
            return direct;
        };
        if (blackList.hasOwnProperty(suffix)) {
            return tunnel;
        };
        pos = host.lastIndexOf(".", pos - 1);
    };

    var IP = dnsResolve(host);

    if (!IP) {
        return tunnel;
    };

    var atom = IP.split(".");
    var code = ((atom[1] & 0xff) << 8) | ((atom[2] & 0xff));
    var hash = atom[0];

    var codeList=[__codeList__];
    var maskList=[__maskList__];

    var codeHash = codeList[hash];
    var maskHash = maskList[hash];

    if (codeHash === 0) {
        return tunnel;
    };

    var min = 0;
    var max = codeHash.length;

    while (min + 1 < max) {
        var mid = (min + max) >> 1;
        codeHash[mid] > code ? max = mid : min = mid;
    };

    if (code - codeHash[min] >> maskHash[min] == 0) {
        return direct;
    };

    return tunnel;
};
