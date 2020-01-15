# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer Sequence',
    'version': '1.1',
    'summary': 'Generate Customer Code',
    'author': 'Srikesh Infotech',
    'license': "AGPL-3",
    'website': 'http://www.srikeshinfotech.com',
    'price': 13,
    'currency': 'EUR',
    'description': """
        Generate Customer Code
    """,
    'images': ['images/main_screenshot.png'],
    'category': "Sales",
    'depends': ['sale', 'point_of_sale'],
    'qweb': ['static/src/xml/pos.xml'],
    'data': ['views/customer_code_view.xml',
             'views/pos_event_templates.xml'
             ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
