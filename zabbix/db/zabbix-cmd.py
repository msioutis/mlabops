#!/usr/bin/python

import zabbix_api
import zabbix_sync
import sys
import pprint
import getpass
from argparse import ArgumentParser, RawTextHelpFormatter

from planetlab import session
from slices import *
from sites  import *


def main():
    parser = ArgumentParser(description="This script interacts with Zabbix server to do some sync up with M-Lab "
                                        "ops db or extracts collected values from Zabbix DB.")
    parser.add_argument("-u", "--user", dest="username", default="admin",
                        help="zabbix username (default is admin)")
    parser.add_argument("-p", "--pass", dest="password",
                        help="zabbix password (if you don't specify this option, you will be prompted for a password)")
    parser.add_argument("-z", "--zabbix-url", dest="url", default="http://localhost/zabbix",
                        help="zabbix server URL (default is http://localhost/zabbix)")
    parser.add_argument("-q", "--quiet",
                        action="store_false", dest="show_logs", default=True,
                        help="don't print the logs to stdout")

    subparser = parser.add_subparsers(dest='action')
    sync_parser = subparser.add_parser("sync",
                                       add_help=False,
                                       description="Syncs Zabbix server with ops DB. It only adds new sites, nodes and slices.")

    remove_parser = subparser.add_parser("remove",
                                         add_help=False,
                                         description="Removes a site, a node or a slice.")
    remove_parser.add_argument("-y", "--yes",
                               action="store_true", dest="im_sure", default=False,
                               help="don't prompt for confirmation")
    remove_parser.add_argument("object_type", choices=["site", "node", "host"],
                               help="type of object which is going to be removed")
    remove_parser.add_argument("object_name",
                               help="actual name of the site, node or host")

    get_parser = subparser.add_parser("get",
                                      formatter_class=RawTextHelpFormatter,
                                      add_help=False,
                                      description="Gets collected data from Zabbix server.")
    get_parser.add_argument("-k", "--key", dest="key",
                            required=True,
                            help="the Zabbix key of the requested value")
    #get_parser.add_argument("-t", "--type", dest="value_type",
    #                        choices=["f","c","l","n","s"],
    #                        required=True,
    #                        help="the value type of the key:\n"
    #                             "    f: Numeric (float)\n"
    #                             "    c: Character\n"
    #                             "    l: Log\n"
    #                             "    n: Numeric (unsigned)\n"
    #                             "    s: Text\n"
    #                       )
    get_parser.add_argument("-h", "--host", dest="host",
                            help="the requested host")
    get_parser.add_argument("-f", "--from", dest="time_from",
                            help="values that have been received after or at the given time")
    get_parser.add_argument("-t", "--till", dest="time_till",
                            help="values that have been received before or at the given time")
    get_parser.add_argument("-l", "--list", dest="list_keys",
                            action="store_true", default=False,
                            help="only lists available keys for the host")

    if len(sys.argv) == 1:
        parser.print_help()
        print
        sync_parser.print_help()
        print
        remove_parser.print_help()
        print
        get_parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    password = args.password
    if password is None:
        password = getpass.getpass('Enter Zabbix Password for %s: ' % args.username)
    
    if args.show_logs: 
        print "Setup zabbix session..."
    z = zabbix_sync.ZabbixSync(server=args.url, username=args.username, password=password)

    # always setup the configuration for everything (very fast)
    if args.show_logs: 
        print "Loading slice & site configuration..."
    for sslice in slice_list:
        for site in site_list:
            for host in site['nodes']:
                h = site['nodes'][host]
                sslice.add_node_address(h)

    if args.action == "sync":
        print "Checking hostgroups..."
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

        print "Checking templates..."
        z.getTemplate(name=z.template_nodes, templates=[])
        z.getTemplate(name=z.template_slices, templates=[])
        for sslice in slice_list:
            z.getTemplate(name=z.template_of_slice % sslice['name'], templates=[z.template_slices])

        print "Creating proxies..."
        for site in site_list:
            for node in site['nodes']:
                z.getProxy(name=z.proxy_node % (site['nodes'][node]['index'], site['name']))

        print "Creating hosts..."
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
    elif args.action == "get":
        host = z.api.host.get({'filter':{'host': args.host}})
        if len(host) < 1:
            print >>sys.stderr, 'The requested host could not be found!'
            sys.exit(1)
        hostid = host[0]['hostid']
        if args.list_keys:
            items = z.api.item.get({'hostids': [hostid], 'search': {'key_': args.key}, 'output': 'extend'});
            for i in items:
                print i['itemid'] + "\t" + i['key_']
        else:
            items = z.api.item.get({'hostids': [hostid], 'search': {'key_': args.key}, 'output': 'extend'});
            if len(items) == 0:
                print >>sys.stderr, 'The requested item could not be found!'
                sys.exit(1)
        
            itemids = [i['itemid'] for i in items] 
            data_type = items[0]['data_type']
            if args.time_from is None and args.time_till is None:
                print items[0]['lastvalue']
            else:
                pprint.pprint(z.api.history.get({'history': data_type,
                                                 'itemids': itemids,
                                                 'time_form': args.time_from,
                                                 'time_till': args.time_till,
                                                 'output': 'extend'
                                                }))
    elif args.action == "remove":
        hosts = []
        if args.object_type == 'host': 
            hosts = z.api.host.get({'filter':{'host': args.object_name}, 'output': 'extend'})
        elif args.object_type == 'node':
            hostgroup_name = "Node %s Group" % args.object_name.replace('.measurement-lab.org', '')
            hg = z.api.hostgroup.get({'filter':{'name': hostgroup_name}, 'output': 'extend', 'selectHosts': 'extend'})
            if len(hg) < 1:
                print >>sys.stderr, 'The requested hosts could not be found!'
                sys.exit(1)
            hosts = hg[0]['hosts']
        elif args.object_type == 'site':
            hostgroup_name = "Site %s Group" % args.object_name.replace('.measurement-lab.org', '')
            hg = z.api.hostgroup.get({'filter':{'name': hostgroup_name}, 'output': 'extend', 'selectHosts': 'extend'})
            if len(hg) < 1:
                print >>sys.stderr, 'The requested hosts could not be found!'
                sys.exit(1)

            hosts = hg[0]['hosts']

        if len(hosts) < 1:
            print >>sys.stderr, 'The requested hosts could not be found!'
            sys.exit(1)

        print
        print 'You are about to delete the following hosts:'
        for h in hosts:
            print h['name']
        if not args.im_sure:
            sys.stdout.write('Are you sure? (y/n) ')
            line = sys.stdin.readline().strip()
            args.im_sure = (line == "y" or line == "yes")

        if args.im_sure:
            result = z.api.host.delete([{'hostid': h['hostid']} for h in hosts])
            if len(result['hostids']) == len(hosts):
                print "All hosts deleted successfully."
            else:
                print >>sys.stderr, "Some error occurred in deleting, double check it manually!"

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
