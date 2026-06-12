from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCollectionAlert(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Alert = cls.env["account.collection.alert"]
        cls.Rule = cls.env["account.collection.alert.rule"]
        cls.Move = cls.env["account.move"]
        cls.partner = cls.env["res.partner"].create({"name": "Cliente Demo Cobro"})
        cls._create_default_rules()

    @classmethod
    def _create_default_rules(cls):
        cls.Rule.search([]).unlink()
        cls.rule_low = cls.Rule.create(
            {
                "name": "Riesgo bajo",
                "days_overdue": 7,
                "amount_min": 100.0,
                "risk_level": "low",
            }
        )
        cls.rule_medium = cls.Rule.create(
            {
                "name": "Riesgo medio",
                "days_overdue": 30,
                "amount_min": 500.0,
                "risk_level": "medium",
            }
        )
        cls.rule_high = cls.Rule.create(
            {
                "name": "Riesgo alto",
                "days_overdue": 60,
                "amount_min": 1000.0,
                "risk_level": "high",
            }
        )
        cls.income_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.env.company.id),
                ("account_type", "=", "income"),
            ],
            limit=1,
        )

    def _create_posted_invoice(self, amount, days_overdue):
        today = fields.Date.context_today(self.env.user)
        due_date = today - timedelta(days=days_overdue)
        line_vals = {
            "name": "Servicio de prueba",
            "quantity": 1,
            "price_unit": amount,
        }
        if self.income_account:
            line_vals["account_id"] = self.income_account.id
        invoice = self.Move.create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": due_date,
                "invoice_date_due": due_date,
                "invoice_line_ids": [(0, 0, line_vals)],
            }
        )
        invoice.action_post()
        return invoice

    def _get_alert_for_move(self, move):
        return self.Alert.search([("move_id", "=", move.id)], limit=1)

    def test_invoice_classified_high_risk(self):
        invoice = self._create_posted_invoice(amount=2000.0, days_overdue=65)
        self.Alert.evaluate_collection_alerts()
        alert = self._get_alert_for_move(invoice)
        self.assertTrue(alert)
        self.assertEqual(alert.risk_level, "high")

    def test_invoice_classified_medium_risk(self):
        invoice = self._create_posted_invoice(amount=600.0, days_overdue=35)
        self.Alert.evaluate_collection_alerts()
        alert = self._get_alert_for_move(invoice)
        self.assertTrue(alert)
        self.assertEqual(alert.risk_level, "medium")

    def test_invoice_not_overdue_no_alert(self):
        today = fields.Date.context_today(self.env.user)
        line_vals = {
            "name": "Servicio futuro",
            "quantity": 1,
            "price_unit": 1500.0,
        }
        if self.income_account:
            line_vals["account_id"] = self.income_account.id
        invoice = self.Move.create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": today,
                "invoice_date_due": today + timedelta(days=15),
                "invoice_line_ids": [(0, 0, line_vals)],
            }
        )
        invoice.action_post()
        self.Alert.evaluate_collection_alerts()
        alert = self._get_alert_for_move(invoice)
        self.assertFalse(alert)

    def test_paid_invoice_removes_alert(self):
        invoice = self._create_posted_invoice(amount=2000.0, days_overdue=65)
        self.Alert.evaluate_collection_alerts()
        self.assertTrue(self._get_alert_for_move(invoice))
        payment = self.env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=invoice.ids,
        ).create({})
        payment.action_create_payments()
        self.Alert.evaluate_collection_alerts()
        self.assertFalse(self._get_alert_for_move(invoice))

    def test_manual_recompute(self):
        invoice = self._create_posted_invoice(amount=600.0, days_overdue=35)
        self.rule_medium.action_recompute_alerts()
        alert = self._get_alert_for_move(invoice)
        self.assertTrue(alert)
        self.assertEqual(alert.risk_level, "medium")
        self.Alert._cron_evaluate_collection_alerts()
        alert_after_cron = self._get_alert_for_move(invoice)
        self.assertEqual(alert_after_cron.risk_level, "medium")
