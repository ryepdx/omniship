from openerp.osv import osv, fields
import base64


class OmnishipPrinter(osv.osv_memory):
    _name = 'omniship.printer'
    _columns = {
	'name': fields.char('Name', readonly=True),
	'label_image': fields.binary('Label Image', readonly=True),
    }



    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = {}
	package_obj = self.pool.get('stock.out.package')
        package_ids = context.get('active_ids', [])
	package = package_obj.browse(cr, uid, package_ids)[0]
	file = package['file']
	res = {'name': package['name'], 'label_image': file}
	return res

    def wizard_prepare_shipment_request(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0])
	return True


    def print_label(self, cr, uid, ids, context):
	if not context:
	    context = {}

        datas = {'ids' : context.get('active_ids',[])}
        datas['form'] = {}
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'omniship.label',
            'datas' : datas,
       }
