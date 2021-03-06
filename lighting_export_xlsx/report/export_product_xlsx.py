# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, models
from odoo.exceptions import UserError, ValidationError


class ExportProductXlsx(models.AbstractModel):
    _name = 'report.lighting_export_xlsx.export_product_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        self.with_context(lang=data['lang']).generate_xlsx_report_ctx(workbook, data, objects)

    def generate_xlsx_report_ctx(self, workbook, data, objects):
        template_id = self.env['lighting.export.template'].browse(data.get('template_id'))
        objects = self.env['lighting.product'].browse(data.get('active_ids'))
        if data.get('interval') == 'all':
            active_model = self.env.context.get('active_model')
            active_domain = data.get('context').get('active_domain')
            objects = self.env[active_model].search(active_domain)

        ## base headers with labels replaced and subset acoridng to template
        header = []
        for line in template_id.field_ids.sorted(lambda x: x.sequence):
            item = objects.fields_get([line.field_id.name], ['string', 'type', 'selection'])
            if item:
                field, meta = tuple(item.items())[0]
                if line.label and line.label.strip():
                    meta['string'] = line.label
                meta.update(dict(num=0, subfields=None))
                header.append((field, meta))

        ## generate data and gather header data
        objects_ld = []
        for obj in objects:
            obj_d = {}
            for field, meta in header:
                datum = getattr(obj, field)
                if meta['type'] == 'selection':
                    datum = dict(meta['selection']).get(datum)
                elif meta['type'] == 'many2many':
                    datum = ','.join([x.display_name for x in datum])
                elif meta['type'] == 'boolean':
                    datum = _('Yes') if datum else _('No')
                elif meta['type'] == 'many2one':
                    datum = datum.display_name
                elif meta['type'] == 'one2many':
                    if hasattr(datum, 'export_xlsx'):
                        datum = datum.export_xlsx(template_id)
                    else:
                        datum = None  # NOT SUPPORTED

                if meta['type'] != 'boolean' and not datum:
                    datum = None

                if isinstance(datum, (tuple, list)):
                    subfields = []
                    for sf in datum:
                        sf1 = sf.keys()
                        if subfields:
                            if subfields != sf1:
                                raise Exception("Unexpected Error")
                        else:
                            subfields = sf1

                    meta['num'] = max(meta['num'], len(datum))
                    meta['subfields'] = subfields
                else:
                    if not meta['num'] and datum:
                        meta['num'] = 1

                obj_d[field] = datum

            objects_ld.append(obj_d)

        ## generate xlsx headers according to data
        xlsx_header = []
        for field, meta in header:
            if not meta['num'] and data.get('hide_empty_fields'):
                continue
            if not meta['subfields']:
                xlsx_header.append(meta['string'])
            else:
                for i in range(1, meta['num'] + 1):
                    field1 = [meta['string']]
                    if meta['num'] > 1:
                        field1.append('%i' % i)
                    for sf in meta['subfields']:
                        xlsx_header.append('%s/%s' % (''.join(field1), sf))

        ## write to xlsx
        sheet = workbook.add_worksheet(template_id.display_name)
        row = col = 0

        # write header to xlsx
        bold = workbook.add_format({'bold': True})
        for col_header in xlsx_header:
            sheet.write(row, col, col_header, bold)
            col += 1

        # write data to xlsx according to header multiplicity
        row = 1
        for obj in objects_ld:
            col = 0
            for field, meta in header:
                if not meta['num'] and data.get('hide_empty_fields'):
                    continue
                if not meta['subfields']:
                    sheet.write(row, col, obj[field])
                    col += 1
                else:
                    num = meta['num']
                    if obj[field]:
                        for so in obj[field]:
                            for dummy, sod in so.items():
                                sheet.write(row, col, sod)
                                col += 1
                            num -= 1
                    col += num * len(meta['subfields'])
            row += 1
