import openerp.addons.decimal_precision as dp
from openerp import api, fields, models
from openerp.tools.translate import _
import logging
import base64
from datetime import datetime
from openerp.addons.web.controllers.main import Session
from openerp.exceptions import Warning as UserError

class SaleGrupoAndava(models.Model):
    _inherit = 'sale.order'

    supplier_id =  fields.Many2one(
        'res.partner', 'Proveedor',  required=True,
        help="Supplier for current sales order.",
        domain=[('supplier', '=', True)]
    )

    vehicle_id =  fields.Many2one(
        'fleet.vehicle', 'Transporte/Caja',  required=True,
        help="Transport used for current sales order.",
    )


#SaleGrupoAndava end class

