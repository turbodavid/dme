# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Coded by: Jorge Medina (jorge.medina@dmesoluciones.com)
############################################################################
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools, release

import os
import time
import tempfile
import base64
from decimal import *
#CSV 
import csv
import psycopg2

#se cambia
class stock_move_split(osv.Model):
    """Inherited"""
    _inherit = 'stock.move.split'

    _columns = {
        'serial_file': fields.binary('Serial File', filters='*.csv', required=False, Store=False)
        #'serial_file_name':fields.char('File Name')
    }

    def onchange_serial_file(self, cr, uid, ids, serial_file_b64str = None, context = None):
        # No selecciono archivo
        if serial_file_b64str == False:
            return False
        else:
            # decodifica el archivo
            file_import = base64.decodestring(serial_file_b64str)
            try:
                # apoyo
                lista = []
                diccionario = {}
                # recorre archivo cada salto de linea
                for row in file_import.split("\n"):
                    if row <> '':
                        # divide las columnas por comas
                        cols = row.split(',')
                        # crea un diccionario por cada registro
                        diccionario = {'name' : cols[0], 'quantity' : Decimal(cols[1])}
                        # los mete en una lista
                        lista.append((0,0,diccionario))
            except:
                raise osv.except_osv("Split Serial", "Exists an error in file, should be a csv file (two columns [serial number, quantity])")
            #regresa la lista con los valores
            return {'value': {'line_ids': lista}}


stock_move_split()