{
    'name': 'Api rest for Sale Order',
    'version': '15.0.0.0.0',
    'summary': 'This is a module for api rest for Sale Order',
    'description': 'Use this module to create sale orders from api rest',
    'author': 'José Carlos Aguilar',
    'company': 'Braintch',
    'maintainer': 'Braintch',
    'website': 'https://www.braintch.net',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/docs.xml',
    ],
    'installable': True,
    'application': False,
}
