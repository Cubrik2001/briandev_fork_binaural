from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    collection_alert_ids = fields.One2many(
        comodel_name="account.collection.alert",
        inverse_name="move_id",
        string="Alertas de cobro",
    )
