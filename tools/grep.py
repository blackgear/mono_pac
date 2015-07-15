import sys
import requests
import re
from collections import Counter

def main(url):
    webpage = requests.get(url).text
    domains = re.findall(r'src="https?://[\w.]*\.(\w*\.\w*)/', webpage)
    results = Counter()
    for domain in domains:
        results[domain] += 1
    for result in results.most_common():
        print(result[0])

if __name__ == '__main__':
    if len(sys.argv) == 1:
        pass
    elif sys.argv[1].startswith('http'):
        main(sys.argv[1])
    else:
        main('http://' + sys.argv[1])
