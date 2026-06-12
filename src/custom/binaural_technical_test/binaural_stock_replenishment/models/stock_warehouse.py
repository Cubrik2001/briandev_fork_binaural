from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    replenishment_responsible_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsable de reabastecimiento",
        help="Usuario asignado a las actividades de reabastecimiento de este almacén.",
    )
