import os
import sys
import logging
from time import sleep
from porkbun_ddns import PorkbunDDNS, cli

logger = logging.getLogger('porkbun_ddns')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

sleep_time = int(os.getenv('SLEEP', 300))
domain = os.getenv('DOMAIN', None)

public_ips = None
if os.getenv('PUBLIC_IPS', None):
    public_ips = [x.strip() for x in os.getenv('PUBLIC_IPS', None).split(',')]
fritzbox = os.getenv('FRITZBOX', None)

config = {
    'secretapikey': os.getenv('SECRETAPIKEY'),
    'apikey': os.getenv('APIKEY')
}

ipv4 = ipv6 = True
if os.getenv('IPV4_ONLY', 'False').lower() in ('true', '1', 't'):
    ipv6 = False
if os.getenv('IPV6_ONLY', 'False').lower() in ('true', '1', 't'):
    ipv4 = False

if os.getenv('DEBUG', 'False').lower() in ('true', '1', 't'):
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)

if os.getenv('INTEGRATION_TEST'):
    print('\n------------------------------------')
    print('INTEGRATION TEST! Printing help menu')
    print('------------------------------------\n')
    while True:
        try:
            cli.main(argv=['-h'])
        except SystemExit:
            pass
        finally:
            print('\n------------------------------------')
            print('Sleeping... {}s'.format(sleep_time))
            print('------------------------------------\n')
            sleep(sleep_time)

if not all([os.getenv('DOMAIN'), os.getenv('SECRETAPIKEY'), os.getenv('APIKEY')]):
    print('Please set DOMAIN, SECRETAPIKEY and APIKEY')
    sys.exit(1)

if not any([ipv4, ipv6]):
    print('You can not set both IPV4_ONLY and IPV6_ONLY to TRUE')
    sys.exit(1)

porkbun_ddns = PorkbunDDNS(config, domain, public_ips=public_ips,
                           fritzbox_ip=fritzbox, ipv4=ipv4, ipv6=ipv6)

while True:
    subdomains = os.getenv('SUBDOMAINS', '')
    if subdomains:
        for subdomain in subdomains.replace(' ', '').split(','):
            porkbun_ddns.set_subdomain(subdomain)
            porkbun_ddns.update_records()
    else:
        porkbun_ddns.update_records()
    print('Sleeping... {}s'.format(sleep_time))
    sleep(sleep_time)
