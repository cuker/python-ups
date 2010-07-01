import urllib, urllib2
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

def dicttoxml(dictionary, parent):
    for key, value in dictionary.iteritems():
        if isinstance(value, dict):
            dicttoxml(value, ET.SubElement(parent, key))
        else:
            ET.SubElement(parent, key).text = unicode(value)

def xmltodict(element):
    ret = dict()
    for item in element.getchildren():
        ret[item.tag] = item.text
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

class StreetAddressValidation(UPSService):
    def make_body(self, address):
        """
        address keys:
            AddressLine
            PoliticalDivision2 #city
            PoliticalDiction #state
            PostcodePrimaryLow #zip
            CountryCode
        """
        root = ET.Element('AddressValidationRequest')
        info = {'Request': {
                    'TransactionReference': {
                        'CustomerContext':'foo',
                        'XpciVersion':'1.0',},
                    'RequestAction':'XAV',
                    'RequestOption':'3'},
                'AddressKeyFormat': address
            }
        dicttoxml(info, root)
        return root
    
    def parse_xml(self, xml):
        ret = dict()
        ret['ambiguous'] = xml.find('.//AmbiguousAddressIndicator') is not None
        ret['valid'] = xml.find('.//ValidAddressIndicator') is not None
        ret['no_candidates'] = xml.find('.//NoCandidatesIndicator') is not None
        ret['classification'] = xmltodict(xml.find('.//AddressClassification'))
        ret['addresses'] = list()
        for item in xml.findall('.//AddressKeyFormat'):
            address = xmltodict(item)
            del address['AddressClassification']
            address['classification'] = xmltodict(item.find('.//AddressClassification'))
            ret['addresses'].append(address)
        return ret

class AddressValidation(UPSService):
    def make_body(self, address):
        """
        address keys:
            AddressLine
            PoliticalDivision2 #city
            PoliticalDiction #state
            PostcodePrimaryLow #zip
            CountryCode
        """
        root = ET.Element('AddressValidationRequest')
        info = {'Request': {
                    'TransactionReference': {
                        'CustomerContext':'foo',
                        'XpciVersion':'1.0',},
                    'RequestAction':'AV',},
                'Address': address
            }
        dicttoxml(info, root)
        return root
    
    def parse_xml(self, xml):
        ret = list()
        for address in xml.findall('.//AddressValidationResult'):
            inner_address = address.find('.//Address')
            info = xmltodict(address)
            del info['Address']
            info.update(xmltodict(inner_address))
            ret.append(info)
        return ret
    
    def execute(self, address):
        addresses = super(AddressValidation, self).execute(address)
        ret = dict()
        ret['addresses'] = addresses
        ret['no_candidates'] = not len(addresses)
        ret['ambiguous'] = len(addresses) > 1
        if 'PostalCode' in address and 'City' in address and 'StateProvinceCode' in address:
            try:
                postal_code = int(address['PostalCode'])
            except ValueError:
                pass
            else:
                ret['valid'] = False
                for possible_address in addresses:
                    if 'PostalCodeHighEnd' in possible_address:
                        try:
                            high = int(possible_address['PostalCodeHighEnd'])
                            low = int(possible_address['PostalCodeLowEnd'])
                        except ValueError:
                            continue
                        else:
                            if (postal_code >= low and 
                                postal_code <= high and
                                address['City'].upper() == possible_address['City'] and
                                address['StateProvinceCode'].upper() == possible_address['StateProvinceCode']):
                                ret['valid'] = True
                                break
        else:
            ret['valid'] = False
            ret['ambiguous'] = True
        return ret

