from ups.common import UPSService, xmltodict, dicttoxml, ET

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
            address['classification'] = xmltodict(item.find('.//AddressClassification'))
            ret['addresses'].append(address)
        return ret

class AddressValidation(UPSService):
    def make_body(self, address):
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
                int_postal_code = int(address['PostalCode'])
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
                            if (int_postal_code >= low and 
                                int_postal_code <= high):
                                possible_address['PostalCode'] = address['PostalCode']
                            if (int_postal_code >= low and 
                                int_postal_code <= high and
                                address['City'].upper() == possible_address['City'] and
                                address['StateProvinceCode'].upper() == possible_address['StateProvinceCode']):
                                ret['valid'] = True
                                break
        else:
            ret['valid'] = False
            ret['ambiguous'] = True
        return ret

