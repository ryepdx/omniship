# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
from openerp import SUPERUSER_ID

class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def _get_delivery_methods(self, cr, uid, order, context=None):
        omni_pool = self.pool.get("omniship")
        processors = omni_pool.browse(
            cr, SUPERUSER_ID, omni_pool.search(cr, uid, [('active', '=', True)]), context=context)

        packages = [
            package for picking in order.picking_ids if picking.state != 'cancel' for package in picking.packages
        ]
        quotes = []
        processor_pool = self.pool.get('omniship.processor')
        carrier_names = list(set([p.service.carrier.lower() for p in processors]))
        processor_dict = dict([(p.service.carrier.lower(), p) for p in sorted(processors, key=lambda x: x.id)])

        if 'fedex' in carrier_names:
            quotes.extend(processor_pool.get_fedex_quotes(cr, uid, packages, context=context))

        if 'usps' in carrier_names:
            quotes.extend(processor_pool.get_usps_quotes(cr, uid, packages, context=context))

        if 'ups' in carrier_names:
            quotes.extend(processor_pool.get_ups_quotes(cr, uid, packages, context=context))

        carrier_ids = []
        service_pool = self.pool.get("delivery.carrier.service")
        carrier_pool = self.pool.get("delivery.carrier")
        carrier_pool.unlink(cr, SUPERUSER_ID, carrier_pool.search(cr, uid, [('sale_id', '=', order.id)]))
        for quote in quotes:
            service_ids = service_pool.search(cr, uid, [('service_code', '=', quote['code'])], context=context)
            if not service_ids:
                continue

            processor = processor_dict[quote['company'].lower()]
            carrier_ids.append(carrier_pool.create(cr, uid, order, {
                'name': '%s %s' % (quote['company'], quote['service']),
                'partner_id': processor.partner_id.id,
                'product_id': processor.product_id.id,
                'normal_price': quote['cost'],
                'website_published': True
            }))

        return super(SaleOrder, self)._get_delivery_methods(cr, uid, order, context=context) + carrier_ids
