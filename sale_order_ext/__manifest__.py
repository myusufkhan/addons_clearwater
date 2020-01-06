{
    'name': "Changes on sale form",

    'summary': """contract terms,datewise delivery """,

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
    'depends': ['base','sale_renting','stock'],

    'data': [
    'views/sale_order_ext.xml',
    'security/ir.model.access.csv',
    'views/stock_move_line_ext.xml',

    ],

}

