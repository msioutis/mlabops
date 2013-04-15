#!/usr/bin/python

import zabbix_api
import zabbix_sync
import sys
import pprint
import getpass

from planetlab import session
from slices import *
from sites  import *


def main():
    username = 'Admin'
    #zabbix_server = 'localhost'
    zabbix_server = 'zabbix-test.measurementlab.net'
    zabbix_path = '/zabbix'

    password = getpass.getpass('Enter Zabbix Password for Admin: ')
     
    print "setup zabbix session"
    z = zabbix_sync.ZabbixSync(server=zabbix_server, path=zabbix_path, username=username, password=password)

    # always setup the configuration for everything (very fast)
    print "loading slice & site configuration..."
    for sslice in slice_list:
        for site in site_list:
            for host in site['nodes']:
                h = site['nodes'][host]
                sslice.add_node_address(h)


    print "checking hostgroups..."
    z.getHostGroup(name=z.hostgroup_all_servers)
    z.getHostGroup(name=z.hostgroup_all_nodes)
    z.getHostGroup(name=z.hostgroup_all_slices)
    for sslice in slice_list:
        z.getHostGroup(name=z.hostgroup_slice % sslice['name'])

    for site in site_list:
        z.getHostGroup(name=z.hostgroup_site % site['name'])

    for site in site_list:
        z.getHostGroup(name=z.hostgroup_site % site['name'])
        for node in site['nodes']:
            z.getHostGroup(name=z.hostgroup_node % (site['nodes'][node]['index'], site['name']))

    print "checking templates..."
    z.getTemplate(name=z.template_nodes, templates=[])
    z.getTemplate(name=z.template_slices, templates=[])
    for sslice in slice_list:
        z.getTemplate(name=z.template_of_slice % sslice['name'], templates=[z.template_slices])

    print "creating proxies..."
    for site in site_list:
        for node in site['nodes']:
            z.getProxy(name=z.proxy_node % (site['nodes'][node]['index'], site['name']))

    print "creating hosts..."
    for site in site_list:
        for node in site['nodes']:
            h = site['nodes'][node]
            z.getHost(name=z.node_hostname % (h['index'], site['name']),
                      visibleName=z.host_node % (h['index'], site['name']),
                      ip=h.interface()['ip'],
                      groups=[z.hostgroup_all_servers,
                              z.hostgroup_all_nodes,
                              z.hostgroup_site % site['name'],
                              z.hostgroup_node % (h['index'], site['name'])],
                      templates=[z.template_nodes],
                      proxy=z.proxy_node % (h['index'], site['name']) 
                     )
            for sslice in slice_list:
                if sslice['index'] != None:
                    i = int(sslice['index'])
                    sp = sslice['name'].split('_')
                    z.getHost(name=z.slice_hostname % (sp[1], sp[0], h['index'], site['name']),
                              visibleName=z.host_slice % (sslice['name'], h['index'], site['name']),
                              ip=h.iplist()[i],
                              groups=[z.hostgroup_all_servers,
                                      z.hostgroup_all_slices,
                                      z.hostgroup_site % site['name'],
                                      z.hostgroup_node % (h['index'], site['name']),
                                      z.hostgroup_slice % sslice['name']],
                              templates=[z.template_of_slice % sslice['name']],
                              macros=[{'macro': '{$VMNAME}', 'value': sslice['name']}],
                              proxy=z.proxy_node % (h['index'], site['name']) 
                             )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
