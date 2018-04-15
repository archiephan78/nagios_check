#!/usr/bin/env python
###RabbitMQ icinga2 check plugin
##chungpht

import json
import httplib
import base64
import sys
from optparse import OptionParser


parser = OptionParser(usage="-H <hostname> -P <port> -u <username> -p <password> -w <warning> -c <critical>")
parser.add_option("-H", "--hostname", action="store", type="string",
                  dest="hostname")
parser.add_option("-P", "--port", action="store", type="string",
                  dest="port")
parser.add_option("-w", "--warning", action="store", type="int",
                  dest="warning")
parser.add_option("-c", "--critical", action="store", type="int",
                  dest="critical")
parser.add_option("-u", "--username", action="store", type="string",
                  dest="username")
parser.add_option("-p", "--password", action="store", type="string",
                  dest="password")
(options, args) = parser.parse_args()


def check_rmq():
    try:
        ret = None
        auth = base64.b64encode("%s:%s" % (options.username, options.password))
        headers = {"Authorization" : "Basic %s" % auth}
        conn = httplib.HTTPConnection(options.hostname, options.port)
        conn.request('GET', '/api/nodes', headers=headers)
        response = conn.getresponse()
        content = response.read()
        conn.close()
        ret = content

        nodes = json.loads(ret)
        ofd=nodes[0]['fd_used']
        lfd=nodes[0]['fd_total']
        ofdp='%.2f' % (100.0*ofd/lfd)
        osd=nodes[0]['sockets_used']
        lsd=nodes[0]['sockets_total']
        osdp='%.2f' % (100.0*osd/lsd)
 

        if float(ofdp) >= options.critical and float(osdp) > options.critical:
            print "CRIT - Too many open files descriptors. Current %f, %f " % (float(ofdp), float(osdp))
            sys.exit(2)
        elif options.warning <= float(ofdp) and float(osdp) <= options.critical:
            print "WARN - Too many open files descriptors. Current %f, %f" % (float(ofdp), float(osdp))
            sys.exit(1)
        else:
            print "OK - RabbitMQ still OK"
            sys.exit(0)
    except Exception:
        print("CRITICAL: Error when connecting to RabbitMQ API")
        sys.exit(2)

if __name__ == '__main__':
    check_rmq()




