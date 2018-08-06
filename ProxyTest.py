# coding=utf-8

import requests

proxies ={
    "http": "http://118.178.227.171:80"
}

r = requests.get("http://ip.chinaz.com/", proxies=proxies)
print(r.text)
