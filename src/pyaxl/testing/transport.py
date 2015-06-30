import os
from suds.transport import Reply
from suds.transport import Transport
from xml.dom.minidom import parseString


class TestingTransport(Transport):

    _output_file = None
    _lastrequest = None

    def define(self, xmlfile):
        """ Define a xml file to use for the reply
            as return value from the send method.
            Format: <xmlfile>_<method>.xml
        """
        self._output_file = xmlfile

    def lastrequest(self):
        """ Returns the last used request which was been sent
            to the callmanager, so that we can validate it
        """
        return self._lastrequest

    def send(self, request):
        """ Returns a fake Reply builded with data from a xml file.
            The xml file must be defined with the method "define"
            before the soap request is send.
        """
        dom = parseString(request.message)
        body = dom.documentElement.getElementsByTagNameNS('*', 'Body')[0]
        method = body.firstChild.localName

        if method.startswith('get'):
            filename = '%s_get.xml' % self._output_file
        elif method.startswith('list'):
            filename = '%s_list.xml' % self._output_file
        elif method.startswith('update'):
            filename = '%s_update.xml' % self._output_file
        elif method.startswith('remove'):
            filename = '%s_remove.xml' % self._output_file
        elif method.startswith('add'):
            filename = '%s_add.xml' % self._output_file
        else:
            filename = '%s.xml' % self._output_file
        with open(os.path.join(os.path.dirname(__file__), 'soap', filename), 'rb') as f:
            message = f.read()
        self._lastrequest = request
        return Reply(200, request.headers, message)
