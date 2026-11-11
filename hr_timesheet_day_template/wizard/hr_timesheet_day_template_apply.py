from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date


class HrTimesheetDayTemplateApply(models.TransientModel):
    _name = 'hr.timesheet.day.template.apply'
    _description = "Appliquer des journées types"

    employee_id = fields.Many2one(
        'hr.employee', string="Collaborateur", required=True,
        default=lambda self: self.env.user.employee_id,
    )
    date_anchor = fields.Date(
        string="Semaine contenant le", required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    day_ids = fields.One2many(
        'hr.timesheet.day.template.apply.line', 'wizard_id', string="Jours",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'day_ids' in fields_list:
            anchor = res.get('date_anchor') or fields.Date.context_today(self)
            res['day_ids'] = self._build_day_lines(anchor)
        return res

    @api.onchange('date_anchor')
    def _onchange_date_anchor(self):
        if self.date_anchor:
            self.day_ids = self._build_day_lines(self.date_anchor)

    @staticmethod
    def _build_day_lines(anchor):
        monday = anchor - timedelta(days=anchor.weekday())
        commands = [(5, 0, 0)]
        for i in range(7):
            commands.append((0, 0, {'date': monday + timedelta(days=i)}))
        return commands

    def action_previous_week(self):
        self.ensure_one()
        self.date_anchor = self.date_anchor - timedelta(days=7)
        self.day_ids = self._build_day_lines(self.date_anchor)
        return self._reopen_self()

    def action_next_week(self):
        self.ensure_one()
        self.date_anchor = self.date_anchor + timedelta(days=7)
        self.day_ids = self._build_day_lines(self.date_anchor)
        return self._reopen_self()

    def _reopen_self(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_apply(self):
        self.ensure_one()
        days_with_template = self.day_ids.filtered('template_id')
        if not days_with_template:
            raise UserError(_("Please select at least one day template to apply."))

        vals_list = []
        for day in days_with_template:
            for line in day.template_id.line_ids:
                vals_list.append({
                    'employee_id': self.employee_id.id,
                    'date': day.date,
                    'project_id': line.project_id.id,
                    'task_id': line.task_id.id,
                    'account_id': line.project_id.account_id.id,
                    'name': line.name or line.project_id.display_name,
                    'unit_amount': line.unit_amount,
                })

        self.env['account.analytic.line'].create(vals_list)
        return {'type': 'ir.actions.act_window_close'}


class HrTimesheetDayTemplateApplyLine(models.TransientModel):
    _name = 'hr.timesheet.day.template.apply.line'
    _description = "Jour de l'assistant d'application de journées types"
    _order = 'date'

    wizard_id = fields.Many2one(
        'hr.timesheet.day.template.apply', required=True, ondelete='cascade',
    )
    # Not readonly at the model level: a readonly field that is never shown
    # for edition (column_invisible in the view) is otherwise dropped from
    # the create/write values sent by the web client when the wizard is
    # saved, which breaks the "required" constraint below.
    date = fields.Date(string="Date", required=True)
    day_name = fields.Char(string="Jour", compute='_compute_day_name')
    template_id = fields.Many2one(
        'hr.timesheet.day.template', string="Journée type",
    )

    @api.depends('date')
    def _compute_day_name(self):
        for line in self:
            line.day_name = format_date(line.env, line.date, date_format='EEEE dd/MM') if line.date else ''
