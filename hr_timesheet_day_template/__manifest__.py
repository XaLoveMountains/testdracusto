{
    'name': "Journées Types - Feuilles de temps",
    'summary': "Modèles de journée type pour accélérer la saisie des feuilles de temps",
    'description': """
Journées types pour les feuilles de temps
==========================================

Permet à chaque collaborateur de créer des "journées types" : un ensemble de
lignes (projet, tâche facultative, durée, description facultative) qu'il
utilise régulièrement (par exemple pour le service de piquet).

Au moment de saisir ses heures, un bouton "Appliquer des journées types"
ouvre un assistant affichant les jours de la semaine. Pour chaque jour, le
collaborateur choisit une journée type (ou laisse vide). Les lignes de la
feuille de temps sont alors créées automatiquement et restent modifiables
comme une saisie manuelle - elles s'ajoutent aux heures déjà présentes, sans
jamais rien écraser.
""",
    'version': '19.0.1.0.0',
    'category': 'Services/Timesheets',
    'depends': ['hr_timesheet', 'timesheet_grid'],
    'data': [
        'security/hr_timesheet_day_template_security.xml',
        'security/ir.model.access.csv',
        'views/hr_timesheet_day_template_views.xml',
        'views/hr_timesheet_day_template_apply_views.xml',
        'views/account_analytic_line_views.xml',
        'views/hr_timesheet_day_template_menus.xml',
    ],
    'demo': [
        'demo/hr_timesheet_day_template_demo.xml',
    ],
    'license': 'LGPL-3',
    'author': "Custom Development",
    'installable': True,
    'application': False,
    'auto_install': False,
}
