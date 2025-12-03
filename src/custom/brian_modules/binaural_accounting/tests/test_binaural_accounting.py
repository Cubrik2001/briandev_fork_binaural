# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class TestBinauralAccounting(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestBinauralAccounting, cls).setUpClass()
        
        # Crear reglas de descuento
        cls.rule_vip = cls.env['binaural.discount.rule'].create({
            'name': 'Regla VIP',
            'customer_type': 'vip',
            'discount_percentage': 0.20,
            'sequence': 1,
        })
        
        cls.rule_mayorista = cls.env['binaural.discount.rule'].create({
            'name': 'Regla Mayorista',
            'customer_type': 'mayorista',
            'discount_percentage': 0.10,
            'sequence': 2,
        })
        
        cls.rule_default = cls.env['binaural.discount.rule'].create({
            'name': 'Regla Default',
            'customer_type': 'default',
            'discount_percentage': 0.05,
            'sequence': 3,
        })

        # Crear partners
        cls.partner_vip = cls.env['res.partner'].create({
            'name': 'Cliente VIP',
            'customer_type': 'vip',
        })
        
        cls.partner_mayorista = cls.env['res.partner'].create({
            'name': 'Cliente Mayorista',
            'customer_type': 'mayorista',
        })
        
        cls.partner_default = cls.env['res.partner'].create({
            'name': 'Cliente Default',
            'customer_type': 'default', # O dejar vacío si el default es 'default'
        })
        
        cls.partner_no_type = cls.env['res.partner'].create({
            'name': 'Cliente Sin Tipo',
            # No seteamos customer_type, debería tomar default
        })

        # Crear producto
        cls.product = cls.env['product.product'].create({
            'name': 'Producto de Prueba',
            'list_price': 100.0,
        })
        
        # Cuenta para facturas (necesaria para validar)
        cls.account_receivable = cls.partner_vip.property_account_receivable_id

    def create_invoice(self, partner):
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })
        return invoice

    def test_discount_application_vip(self):
        """Prueba que se aplique el 20% de descuento a clientes VIP"""
        invoice = self.create_invoice(self.partner_vip)
        
        # Verificar descuento antes de postear (onchange)
        # Nota: Los onchange no se ejecutan automáticamente en create/write en tests
        # a menos que se use Form, pero aquí probamos la lógica de negocio principal.
        # El método action_post tiene la lógica de re-aplicar el descuento.
        
        invoice.action_post()
        
        line = invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.product)
        self.assertEqual(line.discount, 20.0, "El descuento para VIP debería ser 20%")

    def test_discount_application_mayorista(self):
        """Prueba que se aplique el 10% de descuento a clientes Mayoristas"""
        invoice = self.create_invoice(self.partner_mayorista)
        invoice.action_post()
        
        line = invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.product)
        self.assertEqual(line.discount, 10.0, "El descuento para Mayorista debería ser 10%")

    def test_discount_application_default(self):
        """Prueba que se aplique el 5% de descuento a clientes Default"""
        invoice = self.create_invoice(self.partner_default)
        invoice.action_post()
        
        line = invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.product)
        self.assertEqual(line.discount, 5.0, "El descuento para Default debería ser 5%")

    def test_discount_application_no_type(self):
        """Prueba que se aplique el 5% de descuento a clientes sin tipo definido (fallback a default)"""
        invoice = self.create_invoice(self.partner_no_type)
        invoice.action_post()
        
        line = invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.product)
        self.assertEqual(line.discount, 5.0, "El descuento para cliente sin tipo debería ser 5% (regla default)")

    def test_no_discount_rule(self):
        """Prueba que no se aplique descuento si no hay regla coincidente"""
        # Eliminar regla default para este test
        self.rule_default.unlink()
        
        # Crear un nuevo partner con un tipo que no tiene regla (aunque el selection es fijo, 
        # si forzamos o si eliminamos la regla del tipo 'minorista' por ejemplo)
        
        # Vamos a usar el partner_default, pero ya borramos su regla.
        invoice = self.create_invoice(self.partner_default)
        invoice.action_post()
        
        line = invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.product)
        self.assertEqual(line.discount, 0.0, "No debería haber descuento si no hay regla")

