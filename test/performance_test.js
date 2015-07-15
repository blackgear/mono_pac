var url = "http://example.com";
var host = "example.com";
FindProxyForURL(url, host);

var time = process.hrtime();
var repeat = 1000000;
for (var j = 0; j < repeat; j++) {
    FindProxyForURL(url, host);
}

var diff = process.hrtime(time);
console.log('avg: ' + ((diff[0] * 1e3 + diff[1] * 1e-6) * 1e3 / repeat).toFixed(3) + 'us');
