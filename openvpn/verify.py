#!/usr/bin/python

import sys
import os

log = open('/var/log/openvpn-cert-verify', 'a')
print >>log, sys.argv

if 'peer_cert' in os.environ:
    cinfo = sys.argv[2].split("/")
    cns = [s[3:] for s in cinfo if s.startswith("CN=")]
    if len(cns) == 1 and not "/" in cns[0]:
        stored_cert = open("/etc/openvpn/certs/" + cns[0], 'r').read()
        print >>log, "Stored Cert:\n" + stored_cert
        request_cert = open(os.environ['peer_cert'], 'r').read()
        print >>log, "Requested Cert:\n" + request_cert
        if request_cert == stored_cert:
            print >>log, "Certificate accepted."
            sys.exit(0)

print >>log, "Certificate rejected."
sys.exit(1)
