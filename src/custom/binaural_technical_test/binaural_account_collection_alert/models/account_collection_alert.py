from odoo import api, fields, models


RISK_LEVEL_RANK = {"low": 1, "medium": 2, "high": 3}


class AccountCollectionAlert(models.Model):
    _name = "account.collection.alert"
    _description = "Collection Alert"
    _order = "risk_level desc, days_overdue desc"

    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Factura",
        required=True,
        ondelete="cascade",
        index=True,
    )
    rule_id = fields.Many2one(
        comodel_name="account.collection.alert.rule",
        string="Regla aplicada",
        ondelete="set null",
    )
    risk_level = fields.Selection(
        selection=[
            ("low", "Bajo"),
            ("medium", "Medio"),
            ("high", "Alto"),
        ],
        string="Nivel de riesgo",
        required=True,
    )
    days_overdue = fields.Integer(
        string="Días de atraso",
        compute="_compute_days_overdue",
        store=True,
    )
    amount_residual = fields.Monetary(
        related="move_id.amount_residual",
        string="Monto pendiente",
        store=True,
    )
    currency_id = fields.Many2one(
        related="move_id.currency_id",
        store=True,
    )
    partner_id = fields.Many2one(
        related="move_id.partner_id",
        store=True,
    )
    invoice_date_due = fields.Date(
        related="move_id.invoice_date_due",
        store=True,
    )
    company_id = fields.Many2one(
        related="move_id.company_id",
        store=True,
    )
    name = fields.Char(related="move_id.name", store=True)

    @api.depends("move_id.invoice_date_due")
    def _compute_days_overdue(self):
        today = fields.Date.context_today(self)
        for alert in self:
            if alert.move_id.invoice_date_due:
                delta = today - alert.move_id.invoice_date_due
                alert.days_overdue = max(delta.days, 0)
            else:
                alert.days_overdue = 0

    @api.model
    def _get_matching_rule(self, move, rules):
        today = fields.Date.context_today(self)
        if not move.invoice_date_due or move.invoice_date_due >= today:
            return self.env["account.collection.alert.rule"]
        days_overdue = (today - move.invoice_date_due).days
        amount_residual = move.amount_residual
        matching = rules.filtered(
            lambda r: days_overdue >= r.days_overdue
            and amount_residual >= r.amount_min
        )
        if not matching:
            return self.env["account.collection.alert.rule"]
        return matching.sorted(
            key=lambda r: RISK_LEVEL_RANK.get(r.risk_level, 0),
            reverse=True,
        )[:1]

    @api.model
    def _get_eligible_invoices(self):
        today = fields.Date.context_today(self)
        return self.env["account.move"].search(
            [
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("payment_state", "=", "not_paid"),
                ("invoice_date_due", "<", today),
            ]
        )

    @api.model
    def evaluate_collection_alerts(self):
        rules = self.env["account.collection.alert.rule"].search([("active", "=", True)])
        eligible_moves = self._get_eligible_invoices()
        existing_alerts = self.search([])
        alerts_by_move = {alert.move_id.id: alert for alert in existing_alerts}
        processed_move_ids = set()

        for move in eligible_moves:
            processed_move_ids.add(move.id)
            rule = self._get_matching_rule(move, rules)
            if not rule:
                if move.id in alerts_by_move:
                    alerts_by_move[move.id].unlink()
                continue
            vals = {
                "move_id": move.id,
                "rule_id": rule.id,
                "risk_level": rule.risk_level,
            }
            if move.id in alerts_by_move:
                alerts_by_move[move.id].write(vals)
            else:
                self.create(vals)

        stale_alerts = existing_alerts.filtered(
            lambda a: a.move_id.id not in processed_move_ids
            or a.move_id.payment_state in ("paid", "in_payment", "reversed")
            or a.move_id.state != "posted"
        )
        stale_alerts.unlink()
        return True

    @api.model
    def _cron_evaluate_collection_alerts(self):
        self.evaluate_collection_alerts()
