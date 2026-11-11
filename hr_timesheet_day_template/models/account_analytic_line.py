from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def action_open_apply_day_templates(self):
        """Open the "Apply day templates" wizard.

        Tries to guess the employee and the week currently displayed in the
        timesheet grid from the recordset the button was called on (the
        records matching the grid's current domain/navigation). Falls back
        to the current user's employee and the current week when nothing is
        displayed yet (e.g. an empty week) - the user can still adjust the
        week from the wizard itself.
        """
        timesheets = self.filtered('employee_id')
        employee = False
        if timesheets:
            employees = timesheets.employee_id
            if len(employees) == 1:
                employee = employees

        if not employee:
            employee = self.env.user.employee_id

        if not employee:
            raise UserError(_("No employee is linked to your user account."))

        if timesheets:
            ref_date = min(timesheets.mapped('date'))
        else:
            ref_date = fields.Date.context_today(self)

        return {
            'type': 'ir.actions.act_window',
            'name': _("Apply Day Templates"),
            'res_model': 'hr.timesheet.day.template.apply',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': employee.id,
                'default_date_anchor': ref_date,
            },
        }
