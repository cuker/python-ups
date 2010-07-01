import urllib, urllib2
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

from decimal import Decimal

def dicttoxml(dictionary, parent):
    for key, value in dictionary.iteritems():
        if isinstance(value, dict):
            dicttoxml(value, ET.SubElement(parent, key))
        elif isinstance(value, list):
            listtoxml(value, ET.SubElement(parent, key))
        else:
            child = ET.SubElement(parent, key)
            if value is not None:
                child.text = unicode(value)

def listtoxml(iterable, parent):
    for value in iterable:
        dicttoxml(value, parent)

def xmltodict(element):
    ret = dict()
    for item in element.getchildren():
        if item.text:
            ret[item.tag] = item.text
        elif item.find('.//MonetaryValue'):
            ret[item.tag] = Decimal(item.find('.//MonetaryValue').text)
        elif item.find('.//Weight'):
            ret[item.tag] = Decimal(item.find('.//Weight').text)
    return ret

class UPSXMLError(Exception):
    def __init__(self, element):
        self.info = xmltodict(element)
        super(UPSXMLError, self).__init__(self.info['ErrorDescription'])

class UPSService(object):
    def __init__(self, url, user_id, password, license_number):
        self.url = url
        self.user_id = user_id
        self.password = password
        self.license_number = license_number
    
    def make_header(self):
        root = ET.Element('AccessRequest')
        info = {'AccessLicenseNumber':self.license_number,
                'UserId':self.user_id,
                'Password':self.password}
        dicttoxml(info, root)
        return root
    
    def submit_xml(self, xml):
        response = urllib2.urlopen(self.url, xml)
        root = ET.parse(response).getroot()
        if root.tag == 'Error':
            raise UPSXMLError(root)
        error = root.find('.//Error')
        if error:
            raise UPSXMLError(error)
        return root
    
    def make_xml(self, address):
        header = ET.tostring(self.make_header())
        body = ET.tostring(self.make_body(address))
        return u'<?xml version="1.0"?>\n%s\n<?xml version="1.0"?>\n%s' % (header, body)
    
    def execute(self, address):
        xml = self.make_xml(address)
        return self.parse_xml(self.submit_xml(xml))
