import os
import sys
import pyaxl
import shutil
import logging
import fnmatch
import argparse

from suds.xsd import doctor
from suds.client import Client
from suds.reader import Reader
from suds.cache import ObjectCache
from suds.plugin import MessagePlugin
from suds.transport.http import HttpAuthenticated


FILE_PREFIX = 'file://%s'
AXLAPI = 'AXLAPI.wsdl'

Logger = logging.Logger('pyaxl')


def mangle_patch(self, url, x):
    """
    Mangle the name by hashing the I{name} and appending I{x}.
    @return: the mangled name.
    """
    version, filename = url.rsplit('/')[-2:]
    return '%s-%s-%s' % (version, filename, x)
Reader.mangle = mangle_patch
Logger.warning('"suds.reader.Reader.mangle" patched')


class AXLImportDoctor(doctor.ImportDoctor):
    """ Reads automatically XSD Schema from a given path.
    """

    def __init__(self, xsd_location):
        self.xsd_location = xsd_location
        super(AXLImportDoctor, self).__init__(*self.imports())

    def imports(self):
        imports = list()
        for i in os.listdir(self.xsd_location):
            xsd = os.path.join(self.xsd_location, i)
            if fnmatch.fnmatch(xsd, '*.xsd'):
                imports.append(doctor.Import(FILE_PREFIX % xsd))
        return imports


class DebugTransportPlugin(MessagePlugin):
    """ special http transport that will ask for sending each
        request.
    """

    def sending(self, context):
        print('\n\n')
        print('=' * 100)
        print(context.envelope)
        print('=' * 100)
        msg = '\nAre you sure you want to send this request to callmanager? [yes|no]'
        if input(msg).lower() in ('yes', 'y'):
            return super(DebugHttpAuthenicated, self).send(request)
        print('request aborted!')
        sys.exit(1)


class AXLClient(Client):
    """ AXL client to handle all soap request to callmanager.
    """

    clients = dict()

    def __init__(self, configname='default'):

        wsdl = None
        importdoctor = None
        config = pyaxl.configuration.registry.get(configname)
        if config.schema_path is None:
            modpath = os.path.dirname(pyaxl.__file__)
            cachefiles = os.path.join(get_cache_path(configname), 'files')
            if not os.path.exists(cachefiles):
                print('Cache for configuration "%s" doesn\'t exist. Use pyaxl_import_wsdl_to create it first!' % configname,
                      file=sys.stderr)
                raise Exception('Path for cache doesn\'t exist')
            with open(cachefiles) as f:
                wsdl = f.readline().strip()
                importdoctor = doctor.ImportDoctor(*[doctor.Import(l.strip()) for l in f.readlines()])
        else:
            schema_path = config.schema_path
            wsdl = os.path.join(schema_path, AXLAPI)
            if not os.path.exists(wsdl):
                raise ValueError('The version %s is not supported. WSDL was not found.' % config.version)
            wsdl = FILE_PREFIX % wsdl
            importdoctor = AXLImportDoctor(schema_path)
        httpconfig = dict(username=config.user, password=config.passwd, proxy=config.proxy)
        transport = HttpAuthenticated(**httpconfig)
        plugins = list()
        if config.transport_debugger:
            plugins.append(DebugTransportPlugin())

        kwargs = dict(cache=get_cache(configname),
                      location='%s/%s' % (config.host, config.path),
                      doctor=importdoctor,
                      plugins=plugins,
                      transport=transport)
        kwargs.update(config.suds_config)
        super(AXLClient, self).__init__(wsdl, **kwargs)

    @classmethod
    def get_client(cls, configname='default', recreate=False):
        """ return a single instance of client for each configuration.
        """
        client = None
        if configname not in cls.clients or recreate:
            client = AXLClient(configname)
        return cls.clients.setdefault(configname, client)


def get_cache_path(configname):
    name = '%s.cache' % configname
    return os.path.join(os.path.dirname(pyaxl.__file__), 'cache', name)


def get_cache(configname):
    return ObjectCache(get_cache_path(configname))


def import_wsdl():
    parser = argparse.ArgumentParser(description='''Import Cisco's WSDL. The WSDL must be in a
                                                    directory with the version as his name. All
                                                    additional XSD must be in the same directory.''')
    parser.add_argument('-c', '--configname', type=str, default='default', dest='configname',
                        help='''Name of the configuration because pyaxl support multiple
                                configuration. Empty for the default configuration name.''')
    parser.add_argument('-p', '--purge', default=False, dest='purge', action='store_true',
                        help='''Purge old cache files if already exists''')
    parser.add_argument('source', metavar='AXLAPI.wsdl', type=str,
                        help='Path to AXLAPI.wsdl')
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print('AXL doesn\'t exist', file=sys.stderr)
        sys.exit(1)

    source = os.path.abspath(args.source)
    doctor = AXLImportDoctor(os.path.dirname(source))
    cache = get_cache(args.configname)

    if os.path.exists(os.path.join(cache.location, 'files')):
        if args.purge:
            shutil.rmtree(cache.location)
            print('WSDL cache at %s cleared' % cache.location)
        else:
            print('Fail: cache of WSDL already exist. Use -p to purge it.', file=sys.stderr)
            sys.exit(1)

    client = Client(FILE_PREFIX % source, cache=cache, doctor=doctor)
    with open(os.path.join(client.options.cache.location, 'files'), 'w') as f:
        f.write('%s\n' % client.wsdl.url)
        for imp in doctor.imports:
            f.write('%s\n' % imp.ns)
        f.close()
