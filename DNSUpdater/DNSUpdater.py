from __future__ import print_function
import urllib
import requests
from bs4 import BeautifulSoup
from boto.route53.connection import Route53Connection
import re

#config
from config import settings

res = requests.get(settings['router_url'])
if res.status_code == 401:
    #tp-link
    headers = {'Referer': settings['router_url']}
    res = requests.get(settings['router_url'] + '/userRpm/StatusRpm.htm', auth=('admin', 'admin'), headers=headers)

    match = re.search("wanPara = new Array\\(([^\\)]*)\\)", res.text)
    ip = match.group(1).split(', ')[2].replace('"', '')
else:
    soup = BeautifulSoup(res.text)
    ip = soup.find(id="wan_ipaddr").contents[0]

last_ip = None

try:
    file = open('lastLocalIp.txt', 'r')
    last_ip = file.read().rstrip()
except:
    pass

if last_ip != ip:
    if settings['aws_key']:
        route53 = Route53Connection(settings['aws_key'], settings['aws_secret'])
        zone = route53.get_zone(settings['zone']['domain'])
        zone.update_a(settings['zone']['record'], ip)

    s = requests.Session()
    res = s.post("https://www.anveo.com/logina.asp", "txtAction=save&txtUrl=&atl=Sun+Oct+20+22%3A29%3A26+UTC-0200+2013%5BSunday%2C+October+20%2C+2013+10%3A29%3A26+PM%5D&txtEmail=" + urllib.quote_plus(settings['anveo']['email']) + "&txtPassword=" + urllib.quote_plus(settings['anveo']['password']) + "&submit=Enter", headers = {"Content-Type" : "application/x-www-form-urlencoded"})

    for trunk in settings['anveo']['trunks']:
        res = s.get("https://www.anveo.com/_outboundTrunksEdit.asp?txtFormSKey=" + str(trunk[1]) + "&s=&txtAction=save&title=Prime%20Route&prefix=" + urllib.quote_plus(trunk[0]) + "&cap=0.5&concurrent_calls_limit=&notes=&ips=" + ip + "%0A&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&provider_ids=&is_rate_cap_set=1&is_concurrent_calls_limit_set=0&type_id=100&provider_select_type_id=2&depth=5&call_order_type_id=2&")

    f = open('lastIp.txt','w')
    print(ip, file=f)
    f.close()