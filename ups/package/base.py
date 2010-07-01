from ups.common import UPSService, xmltodict, dicttoxml, ET
from decimal import Decimal

class ShipmentConfirm(UPSService):
    def make_body(self, shipment):
        root = ET.Element('ShipmentConfirmRequest')
        info = {'Request': {
                    'TransactionReference': {
                        'CustomerContext':'foo',
                        'XpciVersion':'1.0',},
                    'RequestAction':'ShipConfirm',
                    'RequestOption':'nonvalidate'},
                'Shipment': shipment,
                'LabelSpecification': {
                    'LabelPrintMethod': {'Code':'GIF'},
                    'HTTPUserAgent':'',
                    'LabelImageFormat': {'Code':'GIF'},
                }
            }
        dicttoxml(info, root)
        return root
    
    def parse_xml(self, xml):
        ret = dict()
        ret['ShipmentCharges'] = xmltodict(xml.find('.//ShipmentCharges'))
        ret['BillingWeight'] = Decimal(xml.find('.//BilllingWeight/Weight').text)
        ret['ShipmentIdentificationNumber'] = xml.find('.//ShipmentIdentificationNumber').text
        ret['ShipmentDigest'] = xml.find('.//ShipmentDigest').text
        return ret

class ShipmentAccept(UPSService):
    def make_body(self, shipment_digest):
        root = ET.Element('ShipmentAcceptRequest')
        info = {'Request': {
                    'TransactionReference': {
                        'CustomerContext':'foo',
                        'XpciVersion':'1.0',},
                    'RequestAction':'ShipAccept',
                'ShipmentDigest': shipment_digest,
            }
        dicttoxml(info, root)
        return root
    
    def parse_xml(self, xml):
        ret = dict()
        ret['ShipmentCharges'] = xmltodict(xml.find('.//ShipmentCharges'))
        ret['BillingWeight'] = xml.find('.//BilllingWeight/Weight').text
        ret['ShipmentIdentificationNumber'] = xml.find('.//ShipmentIdentificationNumber').text
        ret['PackageResults'] = list()
        return ret
