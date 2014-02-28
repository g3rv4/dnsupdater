from __future__ import print_function
import subprocess

from config import settings

#libraries
import requests
from bs4 import BeautifulSoup
from boto.route53.connection import Route53Connection

res = requests.get(settings['router_url'])
soup = BeautifulSoup(res.text)

ip = soup.find(id="wan_ipaddr").contents[0]

last_ip = None

try:
    file = open('lastIp.txt', 'r')
    last_ip = file.read().rstrip()
except:
    pass

if last_ip != ip:
    route53 = Route53Connection(settings['aws_key'], settings['aws_secret'])
    zone = route53.get_zone(settings['zone']['domain'])
    zone.update_a(settings['zone']['record'], ip)

    try:
        subprocess.call('asterisk -rx "sip unregister oficina"', shell=True)
    except: pass

    f = open('lastIp.txt','w')
    print(ip, file=f)
    f.close()

print(ip)