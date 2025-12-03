# -*- coding: utf-8 -*-

from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# 1. Extensión de res.partner (Cliente)
# -------------------------------------------------------------------------

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type = fields.Selection([
        ('minorista', 'Minorista'),
        ('mayorista', 'Mayorista'),
        ('vip', 'VIP'),
        ('default', 'Tipo No Definido'),
    ], string="Tipo de Cliente", default='default',
       help="Clasificación del cliente para aplicar reglas de descuento.")

# -------------------------------------------------------------------------
# 2. Extensión de account.move y account.move.line 
# -------------------------------------------------------------------------

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    customer_type = fields.Selection(
        related='partner_id.customer_type',
        string="Tipo de Cliente",
        store=True,
        readonly=True
    )

    @api.model
    def _get_discount_rule(self, customer_type):
        """Busca la regla de descuento activa para el tipo de cliente dado."""
        rule = self.env['binaural.discount.rule'].search([
            ('customer_type', '=', customer_type)
        ], limit=1, order='sequence, discount_percentage desc')
        
        if not rule and customer_type != 'default':
            rule = self.env['binaural.discount.rule'].search([
                ('customer_type', '=', 'default')
            ], limit=1, order='sequence, discount_percentage desc')
            
        return rule

    @api.onchange('partner_id')
    def _onchange_partner_id_discount(self):
        """Actualiza el descuento en las líneas cuando cambia el cliente."""
        if self.move_type == 'out_invoice' and self.partner_id:
            customer_type = self.partner_id.customer_type or 'default'
            discount_rule = self._get_discount_rule(customer_type)
            
            if discount_rule:

                for line in self.invoice_line_ids:
                    if line.display_type == 'product':
                        line.discount = discount_rule.discount_percentage * 100

    def action_post(self):

        for move in self:
            if move.move_type == 'out_invoice':
                customer_type = move.partner_id.customer_type or 'default'
                discount_rule = self._get_discount_rule(customer_type)

                if discount_rule:

                    discount_pct = discount_rule.discount_percentage * 100
                    
                    _logger.info("Aplicando descuento PRE-VALIDACIÓN: %.2f%% a factura %s" % (
                        discount_pct, move.name))
                    
                    lines_to_update = move.invoice_line_ids.filtered(lambda l: l.display_type == 'product')
                    _logger.info("Lineas a actualizar: %s", len(lines_to_update))
                    lines_to_update.write({'discount': discount_pct})

        return super(AccountMove, self).action_post()

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id_discount(self):
        """Aplica el descuento cuando se selecciona un producto."""
        if self.move_id.move_type == 'out_invoice' and self.move_id.partner_id:
            customer_type = self.move_id.partner_id.customer_type or 'default'
            discount_rule = self.move_id._get_discount_rule(customer_type)
            
            if discount_rule:
                self.discount = discount_rule.discount_percentage * 100