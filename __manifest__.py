# -*- coding: utf-8 -*-
{
    'name': "Employee Mails ",

    'summary': """
        Send mails attachments """,

    'description': """
        Module that allow to send attachment to all selected employees 
    """,

    'author': "Abdalla Adil Dev",

    'category': 'hr',
    'version': '0.1',

    'depends': ['hr','mail','base', ],

    'data': [
        # 'security/ir.model.access.csv',
        'wizard/wiz_employee_mail_view.xml',
        # 'views/views.xml',
    ],
    
}
