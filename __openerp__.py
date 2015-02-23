{
    'name': 'Omniship',
    'version': '1.1',
    'author': 'Kyle Waid',
    'category': 'Sales Management',
    'depends': ['stock_package'],
    'website': 'https://www.gcotech.com',
    'description': """ 
    """,
    'data': [
        'wizard/generate_label.xml',
        'wizard/print_label.xml',
        'views/stock.xml',
        'views/delivery.xml',
        'views/service.xml',
        'views/omniship_config.xml',
        'views/package.xml',
        'views/shape_dimension.xml',
        'views/company.xml',
        'security/ir.model.access.csv',
        'data/services.xml',
        'report.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
 #   'external_dependencies': {
#	'python': ['ups', 'py-endicia'],
#    },
}
