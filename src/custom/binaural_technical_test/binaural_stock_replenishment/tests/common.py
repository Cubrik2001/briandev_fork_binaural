from odoo.tests.common import TransactionCase


class ReplenishmentTestCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ReplenishmentCheck = cls.env["stock.replenishment.check"]
        cls.Activity = cls.env["mail.activity"]
        cls.activity_type = cls.env.ref(
            "binaural_stock_replenishment.mail_activity_type_replenishment"
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location = cls.warehouse.lot_stock_id

    def _create_storable_product(self, name, target_qty, priority="medium", qty=0.0):
        product = self.env["product.template"].create(
            {
                "name": name,
                "type": "product",
                "replenishment_target_qty": target_qty,
                "replenish_priority": priority,
            }
        )
        if qty:
            self.env["stock.quant"].create(
                {
                    "product_id": product.product_variant_id.id,
                    "location_id": self.stock_location.id,
                    "quantity": qty,
                }
            )
        return product

    def _count_replenishment_activities(self, product):
        return self.Activity.search_count(
            [
                ("res_model", "=", "product.template"),
                ("res_id", "=", product.id),
                ("activity_type_id", "=", self.activity_type.id),
            ]
        )
