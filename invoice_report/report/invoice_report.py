import logging
logger = logging.getLogger('report_aeroo')

from openerp.report import report_sxw

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'lines':self.get_lines,
            'convert':self.convert,
            'categories': self.get_categories,
        })
        self.context = context

    def convert(self, value):
        return float(value)

    def get_lines(self, o):
        lines = []
        for line in o.detail_ids:
            lines.append(line)
        return lines

    def get_categories(self, o):
        categories = ''
        for categ in o.category_ids:
            categories = categories + categ.name.decode('utf-8') + ","
        return categories