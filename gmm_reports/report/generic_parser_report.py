import logging
logger = logging.getLogger('report_aeroo')

from openerp.report import report_sxw

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'lines': self.get_movtos,
            'lines2': self.get_movtos2,
        })
        self.context = context

    def get_movtos(self, o):
        lines = []
        for line in o.lines:
            lines.append(line)
        return lines

    def get_movtos2(self, o):
        lines = []
        for line in o.lines2:
            lines.append(line)
        return lines
