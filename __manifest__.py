{
    'name': 'Reserva de Canchas Deportivas',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Sistema de reserva de canchas deportivas online y presencial',
    'description': """
        Sistema completo para gestión de reservas de canchas deportivas
        ================================================================
        
        Características principales:
        * Gestión de canchas deportivas
        * Reservas online y presenciales
        * Control de disponibilidad en tiempo real
        * Gestión de clientes
        * Reportes y estadísticas
        * Control de usuarios (Admin y Staff)
        * Dashboard interactivo
    """,
    'author': 'Tu Nombre',
    'website': 'https://www.tuempresa.com',
    'depends': ['base', 'mail', 'portal', 'website', 'auth_oauth'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/cancha_views.xml',
        'views/reserva_views.xml',
        'views/cliente_views.xml',
        'views/menu_views.xml',
        'data/auth_oauth_data.xml',
        'views/portal_templates.xml',
        'views/portal_templates_2.xml',
        'views/portal_templates_3.xml',
        'views/dashboard_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'reserva_canchas/static/src/css/reservas.css',
            'reserva_canchas/static/src/js/reservas.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
