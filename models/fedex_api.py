import base64, logging, re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from collections import namedtuple
from company import Customs, CustomsItem
from openerp.osv import osv, fields
from openerp.tools.translate import _
from fedex.services.rate_service import FedexRateServiceRequest
from fedex.services.ship_service import FedexDeleteShipmentRequest, FedexProcessShipmentRequest
from fedex.config import FedexConfig

PACKAGES = [
    ('FEDEX_BOX', 'FedEx Box'),
    ('FEDEX_PAK', 'FedEx Pak'),
    ('FEDEX_TUBE', 'FedEx Tube'),
    ('YOUR_PACKAGING', 'Custom')
]

SERVICES = [
    ('STANDARD_OVERNIGHT', 'FedEx Standard Overnight'),
    ('PRIORITY_OVERNIGHT', 'FedEx Priority Overnight'),
    ('FEDEX_GROUND', 'FedEx Ground'),
    ('FEDEX_EXPRESS_SAVER', 'FedEx Express Saver')
]


Label = namedtuple("Label", ["tracking", "postage", "label", "format"])

class Address(object):
    def __init__(self, name, address, city, state, zip, country, address2='',
                 phone='', email='', is_residence=True, company_name=''):
        self.company_name = company_name or ''
        self.name = name or ''
        self.address1 = address or ''
        self.address2 = address2 or ''
        self.city = city or ''
        self.state = state or ''
        self.zip = re.sub('[^\w]', '', unicode(zip).split('-')[0]) if zip else ''
        self.country = country or ''
        self.phone = re.sub('[^0-9]*', '', unicode(phone)) if phone else ''
        self.email = email or ''
        self.is_residence = is_residence or False

    def __eq__(self, other):
        return vars(self) == vars(other)


class FedExError(Exception):
    pass

class FedEx(object):
    def __init__(self, config):
        self.config = config

    def _prepare_request(self, request, shipper, recipient, packages):
        request.RequestedShipment.DropoffType = 'REQUEST_COURIER'
        request.RequestedShipment.PackagingType = 'YOUR_PACKAGING'  # package.shape.code

        # Shipper contact info.
        # request.RequestedShipment.Shipper.Contact.PersonName = shipper.name or shipper.company_name
        request.RequestedShipment.Shipper.Contact.CompanyName = shipper.company_name or shipper.name
        request.RequestedShipment.Shipper.Contact.PhoneNumber = shipper.phone

        # Shipper address.
        request.RequestedShipment.Shipper.Address.StreetLines = [shipper.address1, shipper.address2]
        request.RequestedShipment.Shipper.Address.City = shipper.city
        request.RequestedShipment.Shipper.Address.StateOrProvinceCode = shipper.state
        request.RequestedShipment.Shipper.Address.PostalCode = shipper.zip
        request.RequestedShipment.Shipper.Address.CountryCode = shipper.country
        request.RequestedShipment.Shipper.Address.Residential = False

        # Recipient contact info.
        request.RequestedShipment.Recipient.Contact.PersonName = recipient.name or recipient.company_name
        request.RequestedShipment.Recipient.Contact.CompanyName = recipient.company_name or ''
        request.RequestedShipment.Recipient.Contact.PhoneNumber = recipient.phone

        # Recipient address
        request.RequestedShipment.Recipient.Address.StreetLines = [recipient.address1, recipient.address2]
        request.RequestedShipment.Recipient.Address.City = recipient.city
        request.RequestedShipment.Recipient.Address.StateOrProvinceCode = recipient.state
        request.RequestedShipment.Recipient.Address.PostalCode = recipient.zip
        request.RequestedShipment.Recipient.Address.CountryCode = recipient.country

        # This is needed to ensure an accurate rate quote with the response.
        request.RequestedShipment.Recipient.Address.Residential = recipient.is_residence
        request.RequestedShipment.EdtRequestType = 'NONE'

        # Who pays for the shipment?
        # RECIPIENT, SENDER or THIRD_PARTY
        request.RequestedShipment.ShippingChargesPayment.PaymentType = 'SENDER'

        for package in packages:
            wsdl_package = request.create_wsdl_object_of_type('RequestedPackageLineItem')
            wsdl_package.PhysicalPackaging = 'BOX'

            wsdl_package.Weight = request.create_wsdl_object_of_type('Weight')
            wsdl_package.Weight.Value = round(package.weight, 2)
            wsdl_package.Weight.Units = 'LB'

            # wsdl_package.Dimensions = request.create_wsdl_object_of_type('Dimensions')
            #wsdl_package.Dimensions.Length = package.length
            #wsdl_package.Dimensions.Width = package.width
            #wsdl_package.Dimensions.Height = package.height
            #wsdl_package.Dimensions.Units = 'IN'

            request.add_package(wsdl_package)

        return request

    def rate(self, packages, shipper, recipient, insurance='OFF', insurance_amount=0, delivery_confirmation=False,
             signature_confirmation=False):
        response = {'info': []}

        rate_request = FedexRateServiceRequest(self.config)
        rate_request = self._prepare_request(rate_request, shipper, recipient, packages)
        rate_request.RequestedShipment.ServiceType = None
        rate_request.RequestedShipment.EdtRequestType = 'NONE'
        rate_request.RequestedShipment.PackageDetail = 'INDIVIDUAL_PACKAGES'
        rate_request.RequestedShipment.ShippingChargesPayment.Payor.AccountNumber = self.config.account_number

        seen_quotes = []

        try:
            rate_request.send_request()

            for service in rate_request.response.RateReplyDetails:
                for detail in service.RatedShipmentDetails:
                    response['info'].append({
                        'service': service.ServiceType,
                        'package': service.PackagingType,
                        'delivery_day': '',
                        'cost': float(detail.ShipmentRateDetail.TotalNetFedExCharge.Amount)
                    })

        except Exception as e:
            raise FedExError(e)

        return response

    def label(self, package, shipper, recipient, customs=None, image_format="PNG"):
        shipment = self._prepare_request(FedexProcessShipmentRequest(self.config), shipper, recipient, package)

        if package.picking.carrier_id.service_type.name == "international":
            mailclass = 'International'
        else:
            mailclass = 'Priority'

        shipment.RequestedShipment.ServiceType = package.picking.carrier_id.service_type.service_code
        shipment.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = self.config.account_number

        # Specifies the label type to be returned.
        # LABEL_DATA_ONLY or COMMON2D
        shipment.RequestedShipment.LabelSpecification.LabelFormatType = 'COMMON2D'

        # Specifies which format the label file will be sent to you in.
        # DPL, EPL2, PDF, PNG, ZPLII
        shipment.RequestedShipment.LabelSpecification.ImageType = image_format
        shipment.RequestedShipment.LabelSpecification.LabelStockType = 'STOCK_4X6' if image_format == 'EPL2' else 'PAPER_4X6'
        shipment.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'BOTTOM_EDGE_OF_TEXT_FIRST'

        if customs:
            customs_label = shipment.create_wsdl_object_of_type('AdditionalLabelsDetail')
            customs_label.Type = 'CUSTOMS'
            customs_label.Count = 1
            shipment.AdditionalLabels.append(customs_label)

            wsdl_customs = shipment.create_wsdl_object_of_type('CustomsClearanceDetail')
            wsdl_customs.CustomsValue = shipment.create_wsdl_object_of_type('Money')
            wsdl_customs.CustomsValue.Currency = 'USD'
            wsdl_customs.CustomsValue.Amount = package.value

            for item in sorted(customs.items, key=lambda i: i.value, reverse=True):
                wsdl_item = shipment.create_wsdl_object_of_type('Commodity')
                wsdl_item.CustomsValue = shipment.create_wsdl_object_of_type('Money')
                wsdl_item.CustomsValue.Amount = item.value
                wsdl_item.CustomsValue.Currency = 'USD'
                wsdl_item.NumberOfPieces = item.quantity
                wsdl_item.CountryOfManufacture = item.country_of_origin
                wsdl_item.Description = item.description
                wsdl_item.Weight = round(item.weight, 2)
                wsdl_customs.Commodities.append(wsdl_item)

            shipment.CustomsClearanceDetail = wsdl_customs

        try:
            shipment.send_request()

        except Exception as e:
            return {"error": str(e)}

        tracking = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].TrackingIds[0].TrackingNumber
        net_cost = \
            shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].PackageRating.PackageRateDetails[
                0].NetCharge.Amount

        return Label(
            postage=net_cost, tracking=tracking, format=[image_format],
            label=[base64.b64decode(
                shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image)]
        )

    def cancel(self, tracking_no, **kwargs):
        delete = FedexDeleteShipmentRequest(self.config)
        delete.DeletionControlType = "DELETE_ALL_PACKAGES"
        delete.TrackingId.TrackingNumber = tracking_no

        try:
            delete.send_request()
            return delete.response

        except Exception as e:
            raise FedExError(e)


class OmnishipProcessor(osv.osv_memory):
    _inherit = 'omniship.processor'

    def generate_fedex_label(self, cr, uid, package, context=None):
        if context is None:
            context = {}

        package_obj = self.pool.get('stock.out.package')
        omni_obj = self.pool.get('omniship')
        omni_id = omni_obj.search(cr, uid, [('active', '=', True), \
                                            ('carrier', '=', 'fedex')], limit=1)
        if not omni_id:
            raise osv.except_osv(_('Configuration Error!'), \
                                 _("Could not locate a FedEx carrier integration!"))

        omni = omni_obj.browse(cr, uid, omni_id[0])

        self.make_label(cr, uid, omni, package, context)


    def make_label(self, cr, uid, omni, package, customs=None, context=None):
        """
        Wrapper for the make_label method
        """
        package_obj = self.pool.get('stock.out.package')
        
        # Getting the api credentials to be used in shipping label generation
        # endicia credentials are in the format :
        # (account_id, requester_id, passphrase, is_test)
        config = FedexConfig(omni.license_key, omni.password,
                             account_number=omni.account_number,
                             meter_number=omni.meter_number,
                             integrator_id=omni.integrator_id,
                             use_test_server=omni.test_mode
        )
        api = FedEx(config)
        shipper = package.picking.company_id.partner_id
        shipper = Address(shipper.name, shipper.street, shipper.city, shipper.state_id.code,
            shipper.zip, shipper.country_id.code, address2=shipper.street2, phone=shipper.phone
        )
        recipient = package.picking.partner_id
        recipient = Address(recipient.name, recipient.street, recipient.city, recipient.state_id.code,
            recipient.zip, recipient.country_id.code, address2=recipient.street2, phone=recipient.phone
        )

        if not customs:
            customs = {}

        company = self.pool.get("res.users").browse(cr, uid, uid).company_id

        if "items" not in customs:
            customs["items"] = [{
                "description": company.customs_description,
                "quantity": "1",
                "weight": str(package.weight_in_ozs),
                "value": str(package.value) or (str(package.decl_val) if hasattr(package, "decl_val") else None)
            }]

        customs_items = [CustomsItem(
            description=item.get("description") or company.customs_description,
            quantity=str(item.get("quantity") or "1"),
            weight=str(item.get("weight") or package.weight_in_ozs),
            value=str(item.get("value") or package.value) or (str(package.decl_val) if hasattr(package, "decl_val") else None),
            country_of_origin=item.get("country_of_origin") or shipper.country,
        ) for item in customs["items"]]

        customs_obj = Customs(
            signature=customs.get("signature") or company.customs_signature,
            contents_type=customs.get("contents_type") or company.customs_contents_type,
            contents_explanation=customs.get("explanation") or company.customs_explanation,
            commodity_code=customs.get("commodity_code") or company.customs_commodity_code,
            restriction=customs.get("restriction") or company.customs_restriction,
            restriction_comments=customs.get("restriction_comments") or company.customs_restriction_comments,
            undeliverable=customs.get("undeliverable") or company.customs_undeliverable,
            eel_pfc=customs.get("eel_pfc") or company.customs_eel_pfc,
            senders_copy=customs.get("senders_copy") or company.customs_senders_copy,
            items=customs_items
        )

        try:
            label = api.label(cr, uid, package, shipper, recipient, customs=customs_obj, image_format="PNG")

        except FedExError, error:
            raise osv.except_osv(_('Error in generating label'),  _(error))

        package_obj.write(cr, uid, package.id, {
            'name': label.tracking + '.' + label.format.lower(),
            'file': label.label,
            'tracking_number': label.tracking,
            'cost': label.postage,
        })

        return True