from openerp.osv import osv, fields



class StockPicking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'packages': fields.one2many('stock.out.package', 'picking', 'Packages'),
    }
