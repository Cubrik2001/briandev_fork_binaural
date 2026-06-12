from odoo import api, fields, models


class AccountCollectionAlertRule(models.Model):
    _name = "account.collection.alert.rule"
    _description = "Collection Alert Rule"
    _order = "days_overdue, amount_min"

    name = fields.Char(string="Nombre", required=True)
    days_overdue = fields.Integer(string="Días de atraso", required=True, default=0)
    amount_min = fields.Monetary(string="Monto mínimo", required=True, default=0.0)
    risk_level = fields.Selection(
        selection=[
            ("low", "Bajo"),
            ("medium", "Medio"),
            ("high", "Alto"),
        ],
        string="Nivel de riesgo",
        required=True,
        default="low",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        default=lambda self: self.env.company,
        required=True,
    )

    def action_recompute_alerts(self):
        self.env["account.collection.alert"].evaluate_collection_alerts()
        return {
            "type": "ir.actions.act_window",
            "name": "Alertas de cobro",
            "res_model": "account.collection.alert",
            "view_mode": "kanban,tree,form",
            "target": "current",
        }
