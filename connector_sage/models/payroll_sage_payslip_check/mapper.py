# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class PayslipCheckImportMapper(Component):
    _name = 'sage.payroll.sage.payslip.check.import.mapper'
    _inherit = 'sage.import.mapper'

    _apply_on = 'sage.payroll.sage.payslip.check'

    direct = [
        ('ImporteFijo', 'amount'),

        ('CodigoEmpresa', 'sage_codigo_empresa'),
        ('CodigoConvenio', 'sage_codigo_convenio'),
        ('FechaRegistroCV', 'sage_fecha_registro_cv'),
        ('Año', 'sage_ano'),
        ('MesD', 'sage_mesd'),
        ('CodigoEmpleado', 'sage_codigo_empleado'),
        ('FechaCobro', 'sage_fecha_cobro'),
    ]

    @mapping
    def employee_id(self, record):
        external_id = [record['CodigoEmpresa'], record['CodigoEmpleado']]

        binder = self.binder_for('sage.hr.employee')
        employee = binder.to_internal(external_id, unwrap=True)

        assert employee, (
                "employee_id %s should have been imported in "
                "HrEmployeeImporter._import_dependencies" % external_id)

        return {'employee_id': employee.id}

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @only_create
    @mapping
    def payslip_id(self, record):
        return {'payslip_id': self.backend_record.import_payslip_check_id.id}

