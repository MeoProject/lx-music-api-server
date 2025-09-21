import xmltodict


def dumpXML(data):
    return xmltodict.unparse(data)


def loadXML(data):
    return xmltodict.parse(data)
