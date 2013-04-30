
import zabbix_api
import pprint


class ZabbixSync(object):
    hostgroup_all_servers = "All M-Lab Servers Group" 
    hostgroup_all_nodes = "All M-Lab Nodes Group" 
    hostgroup_all_slices = "All M-Lab Slices Group" 
    hostgroup_slice = "Slices of %s Group"
    hostgroup_site = "Site %s Group"
    hostgroup_node = "Node mlab%s.%s Group"
    hostgroup_templates = "M-Lab Templates"

    proxy_node = "mlab%s.%s proxy"

    #template_os_linux = "Template OS Linux"
    #template_mlab_server = "Template M-Lab Server"
    template_nodes = "Template Node"
    template_slices = "Template Slice"
    template_of_slice = "Template of %s Slice"
    #template_vm_host = "libvirt-node"
    #template_vm_vm = "libvirt-vm"

    
    host_node = "Node mlab%s.%s"
    host_slice = "Slice %s of mlab%s.%s"
    
    node_hostname = "mlab%s.%s.measurement-lab.org";
    slice_hostname = "%s.%s.mlab%s.%s.measurement-lab.org";

    hostgroups = {}
    templates = {}
    hosts = {}
    proxies = {}

    api = None

    def __init__(self, server='http://localhost/zabbix', username='Admin', password='zabbix', **kwargs):
        self.api = zabbix_api.ZabbixAPI(server=server)
        self.api.login(user=username, password=password)

    def getHostGroup(self, **kwargs):
        if 'name' not in kwargs:
            raise Exception("'name' is a mandatory argument.")
        name = kwargs['name']
        if name not in self.hostgroups:
            list = self.api.hostgroup.get({'filter':{'name': name}})
            if len(list) == 0:
                print "Trying to create hostgroup '%s'" % name
                result = self.api.hostgroup.create({'name': name})['groupids'][0]
            else:
                result = list[0]['groupid']
            self.hostgroups[name] = result
        return self.hostgroups[name]

    def getProxy(self, **kwargs):
        if 'name' not in kwargs:
            raise Exception("'name' is a mandatory argument.")
        name = kwargs['name']
        if name not in self.proxies:
            list = self.api.proxy.get({'filter':{'host': name}})
            if len(list) == 0:
                print "Trying to create Proxy '%s'" % name
                result = self.api.proxy.create({'host': name, 'status':5})['proxyids'][0]
            else:
                result = list[0]['proxyid']
            self.proxies[name] = result
        return self.proxies[name]

    def getTemplate(self, **kwargs):
        if 'name' not in kwargs:
            raise Exception("'name' is a mandatory argument.")
        if 'templates' not in kwargs:
            kwargs['templates'] = []
        name = kwargs['name']
        if name not in self.templates:
            list = self.api.template.get({'filter':{'host': name}})
            templateids = [{'templateid': self.getTemplate(name=t)} for t in kwargs['templates']]
            if len(list) == 0:
                print "Trying to create template '%s'" % name
                result = self.api.template.create(
                        {'host': name,
                         'groups': [{'groupid': self.getHostGroup(name=self.hostgroup_templates)}],
                         'templates': templateids
                        })['templateids'][0]
            else:
                result = list[0]['templateid']
            self.templates[name] = result
        return self.templates[name]

    def getHost(self, **kwargs):
        if 'name' not in kwargs:
            raise Exception("'name' is a mandatory argument.")
        if 'ip' not in kwargs:
            raise Exception("'ip' is a mandatory argument.")
        if 'groups' not in kwargs:
            raise Exception("'groups' is a mandatory argument.")
        if 'visibleName' not in kwargs:
            kwargs['visibleName'] = None
        if 'templates' not in kwargs:
            kwargs['templates'] = []
        if 'macros' not in kwargs:
            kwargs['macros'] = []
        if 'proxy' not in kwargs:
            kwargs['proxy'] = None

        name = kwargs['name']
        ip = kwargs['ip']
        groups = kwargs['groups']
        visibleName = kwargs['visibleName']
        macros = kwargs['macros']
        proxy = kwargs['proxy']

        if name not in self.hosts:
            list = self.api.host.get({'filter':{'host': name}})
            groupids = [{'groupid': self.getHostGroup(name=gn)} for gn in groups]
            templateids = [{'templateid': self.getTemplate(name=t)} for t in kwargs['templates']]
            if len(list) == 0:
                print "Trying to create host '%s'" % name
                create_opt = {
                              'host': name,
                              'name': visibleName,
                              'interfaces': [{'type': 1,
                                              'main': 1,
                                              'useip': 1,
                                              'ip': ip,
                                              'dns': '',
                                              'port': 10050}],
                              'templates': templateids,
                              'groups': groupids,
                              'macros' : macros
                             }
                if proxy is not None:
                    create_opt['proxy_hostid'] = self.getProxy(name=proxy)
                result = self.api.host.create(create_opt)['hostids'][0]
            else:
                result = list[0]['hostid']
            self.hosts[name] = result
        return self.hosts[name]
