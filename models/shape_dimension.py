from openerp.osv import osv, fields
from openerp.tools.translate import _


class DeliveryBoxShape(osv.osv):
    'Delivery Box Shape'
    _name = 'delivery.box.shape'
    _rec_name = 'complete_name'


    def _name_get_fnc(self, cr, uid, ids, unknown1, unknown2, context=None):
        if not len(ids):
            return {}
        res = []
        records = self.read(cr, uid, ids, ['length', 'width', 'height', 'name'],
            context=context)
        for record in records:
            if not record['name']:
                complete_name = ' x '.join([
                    str(record['length']), str(record['width']), str(record['height'])
                ])
            else:
                complete_name = record['name']

            res.append((record['id'], complete_name))

        return dict(res)


    _columns = {
        'name': fields.char('Name', size=100, required=True),
	'value': fields.char('Value'),
	'carrier': fields.selection([('ups', 'UPS'), ('usps', 'USPS')], 'Carrier', required=True),
        'complete_name': fields.function(_name_get_fnc, method=True,
            type="char", string='Full Name'),
        'length': fields.float('Length', digits=(6,3), required=True),
        'width': fields.float('Width', digits=(6,3), required=True),
        'height': fields.float('Height', digits=(6,3),
            required=True),
    }

