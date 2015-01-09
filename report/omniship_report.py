import time
from openerp.report import report_sxw

class OmnishipLabel(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(OmnishipLabel, self).__init__(cr, uid,
            name, context=context)
        self.localcontext.update({
            'time': time,
        })


class OmnishipForm(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(OmnishipForm, self).__init__(cr, uid,
            name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw(
    'report.omniship.label',
    'stock.out.package',
    'addons/omniship/report/omniship_label.mako',
    parser=OmnishipLabel
)


report_sxw.report_sxw(
    'report.omniship.form',
    'stock.out.package',
    'addons/omniship/report/omniship_form.mako',
    parser=OmnishipForm
)
