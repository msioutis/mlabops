#!/usr/bin/python

from sys import stdin, stdout, exit

data = stdin.readline()
stdout.write("OK\tMy Backend\n")
stdout.flush()

while True:
    data = stdin.readline().strip()
    stdout.write("LOG\t" + data + "\n")
    kind = data.split("\t")[0]

    if kind == "Q":
        kind, qname, qclass, qtype, id, ip = data.split("\t")
        q = qname.replace(".private.", ".")
        f = open('/etc/openvpn/ipp.txt', 'r')
        rip = None
        for line in f:
            line = line.strip()
            if line.startswith(q + ","):
                rip = line[len(q) + 1:]
                break
        if rip != None:
            a, b, c, d = rip.split(".")
            d = str(int(d) + 2)
            rip = "%s.%s.%s.%s" % (a, b, c, d)
            stdout.write("LOG\tDATA\t" + qname + "\t" + qclass + "\tA\t3600\t" + id + "\t" + rip + "\n")
            stdout.write("DATA\t" + qname + "\t" + qclass + "\tA\t3600\t" + id + "\t" + rip + "\n")

    stdout.write("END\n")
    stdout.flush()

