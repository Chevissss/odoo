{
    'name': 'Reserva de Canchas Deportivas',
    'version': '17.0.1.0',
    'category': 'Services',
    'summary': 'Sistema de reserva de canchas deportivas online y presencial',
    'description': """
        Sistema completo para gestión de reservas de canchas deportivas
        Compatible con Odoo 17 y deployado en AWS EC2
    """,
    'author': 'Tu Nombre',
    'website': 'https://www.tuempresa.com',
    'depends': ['base', 'mail', 'portal', 'website'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/cancha_views.xml',
        'views/reserva_views.xml',
        'views/cliente_views.xml',
        'views/menu_views.xml',
        'views/portal_templates.xml',
        'views/portal_templates_2.xml',
        'views/portal_templates_3.xml',
        'views/dashboard_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'reserva_canchas/static/src/css/reservas.css',
        ],
        'web.assets_common': [
            'reserva_canchas/static/src/js/reservas.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
