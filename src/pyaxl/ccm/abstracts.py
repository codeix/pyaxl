import pyaxl
import logging
from copy import copy
from suds.sax.text import Text
from suds.sudsobject import Object

from pyaxl import exceptions
from pyaxl.axlhandler import AXLClient


PF_LIST = 'list'
PF_GET = 'get'
PF_UPDATE = 'update'
PF_ADD = 'add'
PF_REMOVE = 'remove'
XSD_NS = 'ns0'
ESCAPES = dict(cls='class')

log = logging.getLogger('pyaxl')


class BaseCCModel(Object):
    """ Provide base functionality for Abstract
        or XTypes Objects.
    """

    __name__ = ''
    __configname__ = ''
    __config__ = None
    __client__ = None
    __attached__ = False
    __updateable__ = list()

    def __init__(self, *args, **kwargs):
        """ if no arguments are given this object will be created as
            empty object. Else it will find and fetch the data from
            callmanager and fill this object up.
        """
        configname = 'default'
        if 'configname' in kwargs:
            configname = kwargs['configname']
            del kwargs['configname']
        self._configure(configname)
        self._initalize(args, kwargs)

    def __setattr__(self, name, value):
        """ remember which attributes was changed. Generally used for
            the update method.
        """
        if hasattr(self, '__keylist__') and name in self.__keylist__:
            self.__updateable__.append(name)
        super(BaseCCModel, self).__setattr__(name, value)

    @classmethod
    def _axl_method(cls, prefix, name, client):
        """ return a function to call the callmanager.
        """
        return getattr(client.service, '%s%s' % (prefix, name,))

    @classmethod
    def _prepare_result(cls, result, returns):
        """ unwrap suds object as tuple and return a generator.
        """
        unwrapped = result['return']
        if isinstance(unwrapped, str):
            return
        unwrapped = unwrapped[0]
        for obj in unwrapped:
            yield tuple([getattr(obj, r) for r in returns])

    def _initalize(self, args, kwargs):
        """ a part of init method. If some search criteria was found it
            will automatically load this object.
        """
        if not args and not kwargs:
            self._create_empty()
            return
        self._load(args, kwargs)

    def _load(self, args, kwargs):
        """ call the callmanager and load the required object.
        """
        first_lower = lambda s: s[:1].lower() + s[1:] if s else ''
        method = self._axl_method(PF_GET, self.__name__, self.__client__)
        result = method(*args, **kwargs)
        result = getattr(getattr(result, 'return'), first_lower(self.__name__))
        self._loadattr(result)
        self.__attached__ = True

    def _convert_ecaped(self, kw):
        """ convert tags like "cls" to "class". This is normally
            done by suds, but by creating or update an object
            the attribute are not converted. This function will fix it.
        """
        for key, value in kw.items():
            if key in ESCAPES:
                del kw[key]
                kw[ESCAPES[key]] = value
        return kw

    def _skip_empty_tags(self, obj):
        """ callmanager can't handle attributes that are empty.
            This will recursive create a copy of object and remove
            all empty tags.
        """
        copyobj = copy(obj)
        keylist = list()
        for key in obj.__keylist__:
            value = getattr(obj, key)
            if isinstance(value, list):
                copyobj[key] = [i if isinstance(i, Text) else self._skip_empty_tags(i) for i in value]
                keylist.append(key)
            elif isinstance(value, Object):
                copyobj[key] = self._skip_empty_tags(value)
                keylist.append(key)
            else:
                if isinstance(value, Text) and value != '' and value is not None:
                    keylist.append(key)
                else:
                    del copyobj.__dict__[key]
        copyobj.__keylist__ = keylist
        return copyobj

    def _configure(self, configname):
        """ a part of init method. If no name is given it will
            take automatically the name of the class.
        """
        self.__client__ = AXLClient.get_client(configname)
        self.__config__ = pyaxl.configuration.registry.get(configname)
        self.__configname__ = configname
        if self.__name__ is '':
            self.__name__ = self.__class__.__name__

    def _create_empty(self):
        """ create an empty object. All attributes are set
            from a xsd type.
        """
        obj = self.__client__.factory.create('%s:X%s' % (XSD_NS, self.__name__,))
        self._loadattr(obj)

    def _loadattr(self, sudsinst):
        """ merge a suds object in this object... yes, python
            is so powerful :-O

            first: update object attributes with suds attributes.
            second: copy all attributes of class instance to object.

            The result will be a object that has all attributes as theses in XDS.
        """

        self.__dict__.update(sudsinst.__dict__)
        for k in sudsinst.__dict__.keys():
            if hasattr(self.__class__, k):
                self.__dict__[k] = self.__class__.__dict__[k]


class AbstractCCMModel(BaseCCModel):
    """ Base class for all CiscoCallmanager objects.
        This will make the bridge between SUDS and CCM
        objects. In addition all standard method are implement here.
    """

    def create(self):
        """ add this object to callmanager.
        """
        if self.__attached__:
            raise exceptions.CreationException('this object are already attached')
        method = self._axl_method(PF_ADD, self.__name__, self.__client__)
        xtype = self.__client__.factory.create('%s:%s' % (XSD_NS, method.method.name))
        xtype = xtype[1]  # take attributes from wrapper
        tags = xtype.__keylist__ + list(ESCAPES.keys())
        unwrapped = dict()
        for key in self.__keylist__:
            value = getattr(self, key)
            if key in tags and value != '' and value is not None:
                if isinstance(value, Object):
                    unwrapped[key] = self._skip_empty_tags(value)
                else:
                    unwrapped[key] = value
        unwrapped = self._convert_ecaped(unwrapped)
        result = method(unwrapped)
        uuid = result['return']
        self.__attached__ = True
        self._uuid = uuid
        self.__updateable__ = list()
        log.info('new %s was created, uuid=%s' % (self.__name__, uuid,))
        return uuid

    def update(self):
        """ all attributes that was changed will be committed to the callmanager.
        """
        if not self.__attached__:
            raise exceptions.UpdateException('you must create a object with "create" before update')
        method = self._axl_method(PF_UPDATE, self.__name__, self.__client__)
        xtype = self.__client__.factory.create('%s:%s' % (XSD_NS, method.method.name))
        tags = xtype.__keylist__ + list(ESCAPES.keys())
        unwrapped = dict([(i, getattr(self, i),) for i in self.__updateable__ if i in tags])
        unwrapped.update(dict(uuid=self._uuid))
        unwrapped = self._convert_ecaped(unwrapped)
        method(**unwrapped)
        self.__updateable__ = list()
        log.info('%s was updated, uuid=%s' % (self.__name__, self._uuid,))

    def remove(self):
        """ delete this object.
        """
        if not self.__attached__:
            msg = 'This object is not attached and can not removed from callmanager'
            raise exceptions.RemoveException(msg)
        method = self._axl_method(PF_REMOVE, self.__name__, self.__client__)
        method(uuid=self._uuid)
        self._uuid = None
        self.__attached__ = False
        log.info('%s was removed, uuid=%s' % (self.__name__, self._uuid,))

    def reload(self, force=False):
        """ Reload an object.
        """
        if not self.__attached__:
            msg = 'This object is not attached and can not reloaded from callmanager'
            raise exceptions.ReloadException(msg)
        if not force and len(self.__updateable__):
            msg = 'Error because some field are already changed by the client. Use force or update it first.'
            raise exceptions.ReloadException(msg)
        self._load(list(), dict(uuid=self._uuid))

    def clone(self):
        """ Clone a existing object. After cloning the new object will
            be detached. This means it can directly added to the callmanager
            with the create method.
        """
        obj = self.__class__()
        #obj.__dict__.update(self.__dict__)
        for i in ['__updateable__', '__keylist__', ] + self.__keylist__:
            obj.__dict__[i] = copy(getattr(self, i))
        obj._uuid = None
        obj.__attached__ = False
        log.debug('%s was cloned' % self.__name__)
        return obj

    @classmethod
    def list(cls, criteria, returns, skip=None, first=None, configname='default'):
        """ find all object with the given search criteria. It also
            required a list with return values. The return value is a
            generator and the next call will return a tuple with the returnsValues.
        """
        client = AXLClient.get_client(configname)
        method = cls._axl_method(PF_LIST, cls.__name__, client)
        tags = dict([(i, True) for i in returns])
        log.debug('fetch list of %ss, search criteria=%s' % (cls.__name__, str(criteria)))
        args = criteria, tags
        if skip is not None or first is not None:
            if skip is None:
                skip = 0
            if first is None:
                args = criteria, tags, skip
            else:
                args = criteria, tags, skip, first
        return cls._prepare_result(method(*args), returns)

    @classmethod
    def list_obj(cls, criteria, skip=None, first=None, configname='default'):
        """ find all object with the given search criteria.
            The return value is generator. Each next call will
            fetch a new instance and return it as object.
        """
        for uuid, in cls.list(criteria, ('_uuid',), skip, first, configname):
            yield cls(uuid=uuid)


class AbstractXType(BaseCCModel):

    def _initalize(self, args, kwargs):
        """ Xtype is part of soap structure. XType will never be load directly so it's
            need to be created as empty object.
        """
        self._create_empty()

    def _create_empty(self):
        """ create an empty object. All attributes are set
            from a xsd type.
        """
        obj = self.__client__.factory.create('%s:%s' % (XSD_NS, self.__name__,))
        self._loadattr(obj)


class AbstractXTypeListItem(dict):
    """ A special XType that can be used to fill into a list.
    """
    def __init__(self, *args, **kwargs):
        name = self.__class__.__name__
        xtype = type(name, (AbstractXType, self.__class__), dict())(*args, **kwargs)
        self[name[1:]] = xtype
