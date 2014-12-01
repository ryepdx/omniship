from openerp.osv import osv, fields

class DeliveryCarrier(osv.osv):
    _inherit = 'delivery.carrier'
    _columns = {
	'service': fields.many2one('delivery.carrier.service', 'Service'),
    }


