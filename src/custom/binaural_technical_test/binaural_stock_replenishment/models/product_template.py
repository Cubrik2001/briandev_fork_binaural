from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    replenish_priority = fields.Selection(
        selection=[
            ("low", "Baja"),
            ("medium", "Media"),
            ("high", "Alta"),
        ],
        string="Prioridad de reabastecimiento",
        default="medium",
    )
    replenishment_target_qty = fields.Float(
        string="Stock objetivo",
        default=0.0,
    )
    needs_replenishment = fields.Boolean(
        string="Requiere reabastecimiento",
        compute="_compute_needs_replenishment",
        search="_search_needs_replenishment",
    )

    def _compute_needs_replenishment(self):
        for product in self:
            product.needs_replenishment = (
                product.replenishment_target_qty > 0
                and product.qty_available < product.replenishment_target_qty
            )

    def _search_needs_replenishment(self, operator, value):
        if operator not in ("=", "!="):
            return []
        products = self.search([("replenishment_target_qty", ">", 0)])
        matching = products.filtered(
            lambda p: p.qty_available < p.replenishment_target_qty
        )
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("id", "in", matching.ids)]
        return [("id", "not in", matching.ids)]
