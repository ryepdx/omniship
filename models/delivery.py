from openerp.osv import osv, fields

class DeliveryCarrier(osv.osv):
    _inherit = 'delivery.carrier'
    _columns = {
        'service': fields.many2one('delivery.carrier.service', 'Service'),
        'sale_id': fields.many2one('sale.order', 'Sale Order', help='Sale order this quote was retrieved for.')
    }

    def get_price(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for carrier in self.browse(cr, uid, ids, context=context):
            if not carrier.sale_id:
                continue

            res[carrier.id] = {
                'price': carrier.normal_price,
                'available': True
            }

        res.update(super(DeliveryCarrier, self).get_price(
            cr, uid, list(set(ids) - set(res.keys())), field_name, arg=arg, context=context))

        return res