from openerp.osv import osv, fields

class DeliveryCarrier(osv.osv):
    _inherit = 'delivery.carrier'
    _columns = {
        'service': fields.many2one('delivery.carrier.service', 'Service'),
        'quoted_price': fields.float('Quoted Price', help="Price retrieved from shipping API."),
        'sale_id': fields.many2one('sale.order', 'Sale Order', help='Sale order this quote was retrieved for.')
    }
