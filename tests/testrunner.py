import unittest
from pprint import pprint
from ups.addressvalidation import *

USERID = None
PASSWORD = None
LICENSE_NUMBER = None

class TestAddressValidationAPI(unittest.TestCase):
    def test_street_address_validate(self):
        connector = StreetAddressValidation(UPS_XAV_CONNECTION_TEST, USERID, PASSWORD, LICENSE_NUMBER)
        response = connector.execute({'AddressLine':'AIRWAY ROAD SUITE 7',
                                      'PoliticalDivision2':'SAN DIEGO',
                                      'PoliticalDivision1':'CA',
                                      'PostcodePrimaryLow':'92154',
                                      'CountryCode':'US'})
        self.assertEqual(response['addresses'][0]['PoliticalDivision2'], 'SAN DIEGO')
        self.assertEqual(response['addresses'][0]['PoliticalDivision1'], 'CA')
        self.assertTrue(response['ambiguous'])
        self.assertFalse(response['valid'])
        
        response = connector.execute({'AddressLine': '7880 AIRWAY RD',
                                      'CountryCode': 'US',
                                      'PoliticalDivision1': 'CA',
                                      'PoliticalDivision2': 'SAN DIEGO',
                                      'PostcodeExtendedLow': '8308',
                                      'PostcodePrimaryLow': '92154'})
        self.assertFalse(response['ambiguous'])
        self.assertTrue(response['valid'])
    
    def test_address_validate(self):
        connector = AddressValidation(UPS_AV_CONNECTION_TEST, USERID, PASSWORD, LICENSE_NUMBER)
        response = connector.execute({'City':'SAN DIEGO',
                                      'CountryCode':'US',
                                      'StateProvinceCode':'CA',})
        self.assertEqual(response['addresses'][0]['City'], 'SAN DIEGO')
        self.assertEqual(response['addresses'][0]['StateProvinceCode'], 'CA')
        self.assertTrue(response['ambiguous'])
        self.assertFalse(response['valid'])
        
        connector = AddressValidation(UPS_AV_CONNECTION_TEST, USERID, PASSWORD, LICENSE_NUMBER)
        response = connector.execute({'City':'SAN DIEGO',
                                      'CountryCode':'US',
                                      'PostalCode':'92126',
                                      'StateProvinceCode':'CA',})
        self.assertTrue(response['valid'])
        self.assertFalse(response['ambiguous'])
        
        response = connector.execute({'City':'SAN FOO',
                                      'PostalCode':'09837',
                                      'CountryCode':'US',
                                      'StateProvinceCode':'CA',})
        
        self.assertEqual(response['addresses'][0]['City'], 'FPO')
        self.assertEqual(response['addresses'][0]['StateProvinceCode'], 'AE')
        self.assertFalse(response['valid'])

def runtests():
    unittest.main()

if __name__ == '__main__':
    #please append your UPS USERID, PASSWORD, and LICENSE NUMBER to test against the wire
    import sys
    LICENSE_NUMBER, PASSWORD, USERID = sys.argv.pop(), sys.argv.pop(), sys.argv.pop()
    runtests()


