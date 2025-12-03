# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class DiscountRule(models.Model):
    """
    Modelo de configuración para definir reglas de descuento
    automáticas basadas en el tipo de cliente.
    """
    _name = 'binaural.discount.rule'
    _description = 'Regla de Descuento por Tipo de Cliente'
    _order = 'sequence, discount_percentage desc' # Ordenar por secuencia y mayor descuento

    name = fields.Char(string="Nombre de la Regla", required=True)
    sequence = fields.Integer(string="Secuencia", default=10)
    customer_type = fields.Selection([
        ('minorista', 'Minorista'),
        ('mayorista', 'Mayorista'),
        ('vip', 'VIP'),
        ('default', 'Tipo No Definido'), # Para clientes sin tipo
    ], string="Tipo de Cliente", required=True,
       help="Tipo de cliente al que se aplica esta regla de descuento.")
    
    discount_percentage = fields.Float(
        string="Porcentaje de Descuento (%)",
        required=True,
        digits='Discount',
        default=0.0,
        help="Porcentaje de descuento (0.0 a 100.0) a aplicar a las líneas de factura."
    )

    _sql_constraints = [
        ('customer_type_unique', 'unique(customer_type)', 'Ya existe una regla para este Tipo de Cliente. Solo se permite una por tipo.')
    ]

    @api.constrains('discount_percentage')
    def _check_discount_percentage(self):
        """Asegura que el descuento esté entre 0 y 100."""
        for rule in self:
            if not (0.0 <= rule.discount_percentage <= 100.0):
                raise ValidationError("El porcentaje de descuento debe estar entre 0 y 100.")