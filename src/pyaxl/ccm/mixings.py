import logging
import types


log = logging.getLogger('pyaxl')


class MixingAbstractTemplate(object):
    """ Mixing class for all Types with template support.
    """

    @classmethod
    def template(cls, *args, typeclass=None, **kwargs):
        """ return with the given search criteria an complete object.
            On this object all attributes are presetted with the
            values from template.
        """
        template = cls(*args, **kwargs)
        log.debug('%s created from template, criteria: %s, %s' % (cls.__name__, str(args), str(kwargs),))
        obj = template.clone()
        if typeclass is not None:
            obj.cls = typeclass
        return obj


class MixingAbstractLines(object):

    def set_lines(self, lines):
        """ associate a list or a single ccm.Line object
            to deviceprofile.
        """
        if not isinstance(lines, (list, types.GeneratorType)):
            lines = [lines]
        self.lines = list()
        for index, line in enumerate(lines):
            self.lines.append(dict(line=dict(index=index + 1, dirn=dict(_uuid=line._uuid))))

    def set_phonelines(self, xphonelines):
        """ associate a list or a single ccm.XPhoneLine object
            to deviceprofile.
        """
        if not isinstance(xphonelines, list):
            xphonelines = [xphonelines]
        self.lines = list()
        for index, xpl in enumerate(xphonelines):
            xpl.index = index + 1
            self.lines.append(dict(line=xpl))
