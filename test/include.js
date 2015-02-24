function dnsResolve(host) {
    var atom = Array();
    atom.push(Math.random()*224>>0);
    atom.push(Math.random()*256>>0);
    atom.push(Math.random()*256>>0);
    atom.push(Math.random()*256>>0);
    return atom.join(".");
}

function isPlainHostName(host) {
    return host.indexOf(".") === -1;
}

function isInNet(ip, ipstart, ipmask) {
    return false;
}

function shExpMatch(a, b) {
    return false;
}
