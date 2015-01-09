# -*- coding: UTF-8 -*-
"""
    Endicia Integration with openerp

    :copyright: (c) 2011 by Openlabs Technologies & Consulting (P) Ltd.

    :license: AGPL, see LICENSE for more details.
"""

from openerp.osv import osv, fields
from openerp.tools.translate import _


class USPSMailPieceShape(osv.osv):
    'Mail Piece Shapes'
    _name = 'usps.mailpiece.shape'

    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'value': fields.char('value', size=100, required=True),
    }


class MailPieceDimensions(osv.osv):
    'Mail Piece Dimensions'
    _name = 'mailpiece.dimensions'
    _rec_name = 'complete_name'

    def _name_get_fnc(self, cr, uid, ids, unknown1, unknown2, context=None):
        if not len(ids):
            return {}
        res = []
        records = self.read(cr, uid, ids, ['length', 'width', 'height'],
            context=context)
        for record in records:
            complete_name = ' x '.join([
                str(record['length']), str(record['width']), str(record['height'])
            ])
            res.append((record['id'], complete_name))
        return dict(res)

    _columns = {
        'name': fields.char('Name', size=100),
        'complete_name': fields.function(_name_get_fnc, method=True,
            type="char", string='Full Name'),
        'length': fields.float('Length', digits=(6,3), required=True),
        'width': fields.float('Width', digits=(6,3), required=True),
        'height': fields.float('Height(or Thickness)', digits=(6,3),
            required=True),
    }


