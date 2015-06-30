class AXLClientSettings(object):

    def __init__(self, host, user, passwd, path, version,
                 schema_path=None, suds_config=None, proxy=dict(),
                 transport_debugger=False):

        self.host = host
        self.user = user
        self.passwd = passwd
        self.path = path
        self.schema_path = schema_path
        self.suds_config = dict()
        self.proxy = proxy
        self.transport_debugger = transport_debugger
        if suds_config is not None:
            self.suds_config = suds_config
        self.version = '.'.join((str(version).split('.') + ['0'])[:2])


class ConfigurationRegistry(object):

    configurations = dict()

    def register(self, configuration, name='default'):
        self.configurations[name] = configuration

    def get(self, name='default'):
        return self.configurations[name]

registry = ConfigurationRegistry()
