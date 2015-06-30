import re


REGEX_UUID = re.compile(r'^\{?([0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12})\}?$')


def uuid(value):
    """ parse uuid and return a blank uuid without "{}".
        if the uuid is wrong it will raise an exception.
    """
    re = REGEX_UUID.match(value.lower())
    if re is None:
        raise ValueError('uuid is wrong')
    returnvalue, = re.groups()
    return returnvalue


def axlbool(value):
    """ convert suds.sax.text.Text to python bool
    """
    if value is None:
        return None
    if not value:
        return False
    if value.lower() == 'true':
        return True
    return False
