from openerp.osv import osv, fields


class Omniship(osv.osv):
    _name = 'omniship'
    _columns = {
        'carrier': fields.selection([('ups', 'UPS'), ('usps', 'US Postal Service'), ('fedex', 'FedEx')], 'Carrier'),
        'active': fields.boolean('Active'),
        'license_key': fields.char('License Key', size=100),
        'account_number': fields.char('Account Number/Shipper Number', size=100),
        'meter_number': fields.char('Meter Number', size=64),
        'integrator_id': fields.char('Integrator ID', size=64),
        'username': fields.char('Username', size=100),
        'password': fields.char('Password', size=100),
        'test_mode': fields.boolean('Test Mode'),
        'save_xml': fields.boolean('Save XML Messages ?'),
        'weight_uom': fields.selection([('KGS', 'KGS'), ('LBS', 'LBS')], 'Weights UOM'),
        'length_uom': fields.selection([('IN', 'IN'), ('CM', 'CM')], 'Length UOM'),
        'label_image': fields.binary('Label Header Image'),
        'partner_id': fields.many2one('res.partner', 'Transport Company', required=True),
        'product_id': fields.many2one('product.product', 'Delivery Product', required=True),
    }

    _defaults = {
        'active': True,
    }

    def get_ups_credentials(self, cr, uid, omni, context=None):
        return (
            omni.license_key,
            omni.username,
            omni.password,
            omni.test_mode,
            omni.save_xml,
        )


    def get_endicia_credentials(self, cr, uid, omni, context=None):
        return (
            omni.account_number,
            omni.username,
            omni.password,
            omni.test_mode,
        )

    def get_ups_uoms(self, cr, uid, omni, context=None):
        """Returns the codes of weight and length UOM used by UPS
        """

        return (
            omni.weight_uom,
            omni.length_uom,
        )


    def get_ups_shipper(self, cr, uid, omni, context=None):
        """Returns the UPS Shipper
        """

        return omni.account_number


    def get_ups_save_xml(self, cr, uid, omni, context=None):
        """Returns the UPS Save XML flag
        """

        return omni.save_xml
