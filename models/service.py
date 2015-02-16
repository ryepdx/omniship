from openerp.osv import osv, fields


class DeliveryCarrierService(osv.osv):
    _name = 'delivery.carrier.service'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
#            if context.get('show_carrier'):
            name = '[' + record.carrier.upper() + '] ' + name

            res.append((record.id, name))
        return res


    _columns = {
        'name': fields.char('Name'),
        'active': fields.boolean('Active'),
        'carrier': fields.selection([('ups', 'UPS'), ('usps', 'USPS'), ('fedex', 'FedEx')], 'Carrier', required=True),
        'service_type': fields.selection([
            ('domestic', 'Domestic'),
            ('international', 'International')],
            'Service Type'),
        'service_code': fields.char('Service Code'),
    }


    _defaults = {
	'active': True
    }
