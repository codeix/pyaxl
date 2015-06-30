from xml.dom import minidom


def validateSOAPRequest(request, method, tags):
    """ request: the request used by suds
        method: soap method name, e.g. "getUser"
        tags: a dict with tag name and value, e.g. dict(userid='riols')
    """
    dom = minidom.parseString(request.message)
    assert dom.documentElement.tagName == 'SOAP-ENV:Envelope'
    dom.documentElement.childNodes[0].localName
    header = dom.documentElement.getElementsByTagNameNS('*', 'Header')
    body = dom.documentElement.getElementsByTagNameNS('*', 'Body')
    assert len(header) == 1
    assert len(body) == 1
    body, header = body.pop(), header.pop()
    assert body.firstChild.localName == method
    for tag, value in tags.items():
        nodes = body.getElementsByTagNameNS('*', tag)
        assert len(nodes) == 1
        assert nodes[0].firstChild.nodeValue == value


def _printSOAPRequest(node, level):
    output = list()
    for subnode in node.childNodes:
        spaces = ' ' * 4 * level
        if isinstance(subnode.firstChild, minidom.Text):
            output.append('%s%s=%s' % (spaces, subnode.localName, subnode.firstChild.nodeValue))
        else:
            output.append('%s%s:' % (spaces, subnode.localName))
            output.append(_printSOAPRequest(subnode, level + 1))
    return '\n'.join(output)


def printSOAPRequest(request):
    dom = minidom.parseString(request.message)
    assert dom.documentElement.tagName == 'SOAP-ENV:Envelope'
    dom.documentElement.childNodes[0].localName
    header = dom.documentElement.getElementsByTagNameNS('*', 'Header')
    body = dom.documentElement.getElementsByTagNameNS('*', 'Body')
    assert len(header) == 1
    assert len(body) == 1
    body, header = body.pop(), header.pop()
    nodemethod = body.firstChild

    print('%s:\n%s' % (nodemethod.localName, _printSOAPRequest(nodemethod, 1)))
