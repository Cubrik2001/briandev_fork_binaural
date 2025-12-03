# -*- coding: utf-8 -*-
{
    'name': "Binaural Accounting Extensions",
    'version': '1.0.0',
    'summary': "Módulo de extensión para contabilidad: Reglas de descuento y tipificación de clientes.",
    'category': 'Accounting/Invoicing',
    'author': "Brian Reyes",
    'website': "https://www.binaural.com.ve",
    'license': 'AGPL-3',
    'depends': ['base', 'account'],
    'data': [
        # Seguridad y permisos
        'security/ir.model.access.csv',
        # Vistas de configuración (Reglas)
        'views/discount_rule_views.xml',
        # Extensión de la vista de Partner
        'views/res_partner_views.xml',
        # Extensión de la vista de Factura
        'views/account_move_views.xml',
        'menu/accounting_menu.xml',
    ],
    'installable': True,
    'application': False,
}