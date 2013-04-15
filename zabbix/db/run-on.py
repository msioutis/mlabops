#!/usr/bin/python

import sys
import pprint
import getpass
import subprocess
from argparse import ArgumentParser, RawTextHelpFormatter
from planetlab import session
from slices import *
from sites  import *

domainname_postfix = ".measurement-lab.org"
command = None
args = None
has_error = False

def main():
    global command, args

    parser = ArgumentParser(description="Run shell commands on M-Lab nodes or slices VMs.\n"
                                        "Commands are read from stdin by default and the outputs go to stdout.",
                            epilog="Examples:\n"
                                   "          ./%(prog)s nodes -c 'service nm restart'\n"
                                   "          cat install-agent | ./%(prog)s slices --slice gt_partha\n"
                                   "          ./%(prog)s all -l\n",
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("target", choices=["all", "nodes", "slices"],
                        help="run commands on only nodes, slices (VMs) or both (all)")
    parser.add_argument("-s", "--site", dest="site",
                        help="only runs on servers of SITE (like nuq0t)", metavar="SITE")
    parser.add_argument("-n", "--node", dest="node",
                        help="only runs on servers of NODE (like mlab1.nuq0t)", metavar="NODE")
    parser.add_argument("--slice", dest="slice",
                        help="only runs on VMs of SLICE (like gt_partha)", metavar="SLICE")
    parser.add_argument("-c", "--command", dest="command",
                        help="use COMMAND instead of reading it from stdin", metavar="COMMAND")
    #parser.add_argument("-u", "--user", dest="user", default="root",
    #                    help="ssh USER who runs the commands (default is root)", metavar="ROOT")
    parser.add_argument("-l", "--list",
                        action="store_true", dest="list", default=False,
                        help="only prints matching servers and does NOT run any commands")
    parser.add_argument("-x", "--show-commands",
                        action="store_true", dest="show_commands", default=False,
                        help="show executing commands, as well as their outputs")
    parser.add_argument("-q", "--quiet",
                        action="store_true", dest="quiet", default=False,
                        help="don't print the output of commands to stdout")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if (args.target == "all" or args.target == "nodes") and args.slice is not None:
        sys.stderr.write("You cannot specify --slice when your target is not 'slices'\n")
        sys.exit(1)

    # always setup the configuration for everything (very fast)
    sys.stderr.write("Loading slice & site configuration...\n")
    for sslice in slice_list:
        for site in site_list:
            for host in site['nodes']:
                h = site['nodes'][host]
                sslice.add_node_address(h)

    if args.slice is not None and not args.slice in [c['name'] for c in slice_list]:
        sys.stderr.write("Unknown slice name: %s\n" % args.slice)
        sys.stderr.write("Available slice names are: \n%s\n" % '\n'.join([c['name'] for c in slice_list]))
        sys.exit(1)

    if args.site is not None and not args.site in [c['name'] for c in site_list]:
        sys.stderr.write("Unknown site name: %s\n" % args.site)
        sys.stderr.write("Available site names are: \n%s\n" % '\n'.join([c['name'] for c in site_list]))
        sys.exit(1)

    if args.node is not None:
        sp = args.node.split(".")
        if len(sp) != 2:
            sys.stderr.write("Incorrect format for node name (It should be like mlab1.nuq0t): %s\n" % args.node)
            sys.exit(1)
        args.site = sp[1]
        s = [c for c in site_list if c['name'] == args.site]
        if len(s) != 1:
            sys.stderr.write("Unknown site name: %s\n" % args.site)
            sys.stderr.write("Available site names are: \n%s\n" % '\n'.join([c['name'] for c in site_list]))
            sys.exit(1)
        if not (args.node + domainname_postfix) in s[0]["nodes"]:
            sys.stderr.write("Unknown node name: %s\n" % args.node)
            sys.stderr.write("Available nodes of %s are: \n%s\n" % 
                                (args.site, '\n'.join([c.replace(domainname_postfix, "") for c in s[0]["nodes"]])))
            sys.exit(1)

    command = None
    if args.command is not None:
        command = args.command
    if command is None and not args.list:
        command = sys.stdin.read()
    
    for site in site_list:
        if args.site is not None and site['name'] != args.site:
            continue
        for node in site['nodes']:
            n = node.replace(domainname_postfix, "")
            if args.node is not None and n != args.site:
               continue

            if args.target == "all" or args.target == "nodes":
                runon(n + domainname_postfix, 'root@' + n + domainname_postfix)

            if args.target == "all" or args.target == "slices":
                for sslice in slice_list:
                    s = sslice['name']
                    if args.slice is not None and s != args.slice:
                        continue
                    sp = s.split('_')
                    if sslice['index'] != None:
                        runon(sp[1] + "." + sp[0] + "." + n + domainname_postfix, s + "@" + n + domainname_postfix)

def runon(server_name, ssh_addr):
    global has_error
    if args.list:
        print server_name
        return
    
    sys.stderr.write("Running command on %s...\n" % server_name)
    process = subprocess.Popen("ssh -T -oStrictHostKeyChecking=no %s" % ssh_addr, shell=True,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output,stderr = process.communicate(input="set -e;set %sx;%s" % ("-" if args.show_commands else "+", command))
    status = process.poll()

    if stderr != None:
        print stderr
    if not args.quiet:
        print output
    if status != 0:
        sys.stderr.write("Error while running command on %s! (%d)\n" % (server_name, status))
        has_error = True

if __name__ == "__main__":
    try:
        main()
        if has_error:
            sys.exit(1)
        sys.exit(0)
    except KeyboardInterrupt:
        pass
