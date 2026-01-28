{
    'name': 'Suscripción de Pan',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Módulo de gestión de suscripciones de pan',
    'description': '''
        Módulo para manejar suscripciones de pan.
        Permite gestionar suscripciones con:
        - Cantidades: 10, 20 o 50 unidades
        - Fechas de inicio y fin
        - Seguimiento de entregas
        - Integración con ventas y stock
        - Facturación automática
    ''',
    'author': 'BreadMoi',
    'depends': ['base', 'sale', 'stock', 'account', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/bread_subscription_views.xml',
        'views/bread_subscription_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
