{
    'name': "Changes on contact form",

    'summary': """Add rental on contact form and all other related data""",

    'description': """
        Nothing much for now.

    """,

    'author': "Comstar USA Inc.",
    'website': "http://www.comstarusa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'contact',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_renting','contacts','stock','industry_fsm'],

    'data': [
    'views/rental_on_contact.xml',

    ],

}

