from openerp.osv import osv, fields


class PurchaseOrder(osv.osv):
    _inherit = 'purchase.order'



    def set_order_line_status(self, cr, uid, ids, status, context=None):
	"""
	For now we override completely the function because the problem exists in line
	if status == 'cancel'
	Open to merge requests for proper super() or other solution
	"""

        line = self.pool.get('purchase.order.line')
        order_line_ids = []
        proc_obj = self.pool.get('procurement.order')
        for order in self.browse(cr, uid, ids, context=context):
            if status in ('draft', 'cancel'):
                order_line_ids += [po_line.id for po_line in order.order_line]
            else: # Do not change the status of already cancelled lines
                order_line_ids += [po_line.id for po_line in order.order_line if po_line.state != 'cancel']
        if order_line_ids:
            line.write(cr, uid, order_line_ids, {'state': status}, context=context)
        if order_line_ids and status == 'cancel':
            procs = proc_obj.search(cr, uid, [('purchase_line_id', 'in', order_line_ids)], context=context)
            if procs:
		#TODO: Add case for MTO transactions
#		proc_obj.write(cr, uid, procs, {'state': 'exception'}, context=context)
                proc_obj.write(cr, uid, procs, {'state': 'cancel'}, context=context)

        return True
