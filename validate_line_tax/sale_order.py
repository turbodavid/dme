# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Coded by: Jorge Alfonso Medina Uriarte <jesus.meza@dmesoluciones.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class sale_order(osv.Model):
    _inherit = 'sale.order'

    def _check_tax_sale_order_line(self, cr, uid, ids, context=None):
        _logger.debug("check %s" % ids)
        resultado = False
        for sale in self.browse(cr, uid, ids, context):
            for line in sale.order_line:
                _logger.debug("sale order line: %s" % line.tax_id)
                if len(line.tax_id)>0:
                    resultado = True
        return resultado
            
    _constraints = [(_check_tax_sale_order_line,"The sale order cannot be without taxes in lines!",['order_line']),]
