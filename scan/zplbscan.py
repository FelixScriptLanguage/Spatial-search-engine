# -*- coding: utf-8 -*-
import sys
from scapy.all import *
def shibiexitong(ip):
    packet = IP(dst=ip)/ICMP()
    result = sr1(packet,timeout=1,verbose=0)
    if result is None:
        print('OS:error')
    elif int(result[IP].ttl) <= 64:
        print('OS:Linux/Unix')
    else:
        print('OS:Windows')
shibiexitong(sys.argv[1])