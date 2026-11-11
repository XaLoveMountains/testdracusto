from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrTimesheetDayTemplate(models.Model):
    _name = 'hr.timesheet.day.template'
    _description = "Journée type (modèle de saisie de feuille de temps)"
    _order = 'name'

    name = fields.Char(string="Nom", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string="Société",
        default=lambda self: self.env.company, required=True,
    )
    employee_ids = fields.Many2many(
        'hr.employee', string="Collaborateurs concernés",
        default=lambda self: self.env.user.employee_id.ids,
        help="Collaborateurs auxquels cette journée type est destinée en "
             "priorité. N'importe quel utilisateur des feuilles de temps "
             "peut néanmoins l'appliquer : ce champ sert uniquement à "
             "filtrer/retrouver facilement les journées types pertinentes, "
             "il ne restreint pas l'accès.",
    )
    line_ids = fields.One2many(
        'hr.timesheet.day.template.line', 'template_id', string="Lignes", copy=True,
    )
    total_hours = fields.Float(
        string="Total (heures)", compute='_compute_total_hours',
    )

    @api.depends('line_ids.unit_amount')
    def _compute_total_hours(self):
        for template in self:
            template.total_hours = sum(template.line_ids.mapped('unit_amount'))

    @api.constrains('line_ids')
    def _check_line_ids(self):
        for template in self:
            if not template.line_ids:
                raise ValidationError(_("A day template must contain at least one line."))


class HrTimesheetDayTemplateLine(models.Model):
    _name = 'hr.timesheet.day.template.line'
    _description = "Ligne de journée type"
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'hr.timesheet.day.template', string="Journée type",
        required=True, ondelete='cascade', index=True,
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(related='template_id.company_id', store=True)
    project_id = fields.Many2one(
        'project.project', string="Projet", required=True,
        domain="[('company_id', 'in', [company_id, False]), ('allow_timesheets', '=', True)]",
    )
    task_id = fields.Many2one(
        'project.task', string="Tâche",
        domain="[('project_id', '=', project_id)]",
    )
    name = fields.Char(string="Description")
    unit_amount = fields.Float(string="Durée (heures)", required=True, default=0.0)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.task_id and self.task_id.project_id != self.project_id:
            self.task_id = False

    @api.constrains('project_id')
    def _check_project_id(self):
        for line in self:
            if line.project_id and not line.project_id.account_id:
                raise ValidationError(_(
                    "Project %(project)s cannot be used in a day template: it has no "
                    "analytic account configured, so no timesheet entry could be "
                    "created from it. Make sure timesheets are enabled on this project.",
                    project=line.project_id.display_name,
                ))

    @api.constrains('unit_amount')
    def _check_unit_amount(self):
        for line in self:
            if line.unit_amount < 0:
                raise ValidationError(_("Duration cannot be negative."))
