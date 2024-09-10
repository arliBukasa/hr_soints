# -*- coding: utf-8 -*-
{
    'name': "hr_soints",

    'summary': """
        gestion des soints de santé des agents
        """,

    'description': """
        ce permet de gerer les soints de santé des agents, aibsi que leurs dependants
        il est destiné aux hopitaux partenaires pour verification des listes.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_employee_updation','hr','website'],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/templates.xml",
        "views/employee_dependant.xml",
        "views/hr_employee_views.xml",
        "views/res_company_views.xml",
        "report/hr_employee_report.xml"
    ],
    'installable': True,
    'application': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}