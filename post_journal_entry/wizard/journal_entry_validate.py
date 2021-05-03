# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import fields, orm
from openerp.tools.translate import _

class journal_entry_validate(orm.TransientModel):
    _name = "journal.entry.validate"
    _description = ""
    #_inherit = 'account.move'
    
    def journal_entries_validate(self, cr, uid, ids, context=None):
        """
        This function Open Journal Entry lines window for validate
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: Journal Entries line select’s ID or list of IDs
        @return: dictionary of PyERP
         """
        # Objeto para realizar las búsquedas de los movimientos seleccionados
        account_move_obj = self.pool.get('account.move')
        
        # Se obtienen los Ids seleccionados
        move_ids = context.get('active_ids', [])
        
        # Se recorre cada uno de los Ids seleccionados
        for id in move_ids:
            # Se obtiene por medio del Id la póliza para poder consultar el estatus
            journal_entry = account_move_obj.browse(cr, uid, id, context=context)
            
            # Se verifica que la Poliza se encuentre en estatus "draft"
            if(journal_entry.state == 'draft'):
                # Se ejecuta el boton de validar
                account_move_obj.button_validate(cr, uid, [id], context=context)
        
        return True