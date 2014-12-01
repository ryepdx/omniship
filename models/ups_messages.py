from osv import osv, fields

STATE_SELECTION = [
    ('draft', 'Draft (Not Processed)'),
    ('confirmed', 'Confirmed'),
    ('accepted', 'Accepted'),
    ('cancelled', 'Cancelled'),
]

MESSAGE_TYPE_SELECTION = [
    ('request', 'Request'),
    ('response', 'Response')
]

class UpsMessage(osv.osv):
    """Model to record all UPS XML messages.
    """

    _name = 'ups.message'
    _description = __doc__

    def _text2bin(self, cursor, user, ids, field_name, arg, context):
        """Create a binary representation of the xml message so that we can be
        able to download it"""

        res = {}
        for message in self.browse(cursor, user, ids, context):
            res[message.id] = base64.b64encode(message.message)

        return res

    _columns = {
        'name': fields.char('Message name', size=50, readonly=True),
        'type': fields.selection(MESSAGE_TYPE_SELECTION,
                                 string='Message type',
                                 type='selection',
                                 readonly=True),
        'message': fields.text('XML Message', readonly=True),
        'message_bin': fields.function(_text2bin, string='XML Message',
                                   type='binary', method=True, readonly=True),
#        'shipping_register_rel': fields.many2one('ups.shippingregister',
#                                                 'Relation Field',
 #                                                readonly=True)
    }

UpsMessage()
