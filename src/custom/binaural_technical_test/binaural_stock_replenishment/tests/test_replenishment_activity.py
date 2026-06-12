from odoo.tests.common import TransactionCase, tagged

from .common import ReplenishmentTestCommon


@tagged("post_install", "-at_install")
class TestReplenishmentActivity(ReplenishmentTestCommon, TransactionCase):
    def test_activity_created_below_target(self):
        product = self._create_storable_product(
            "Product Low Stock", target_qty=10.0, qty=3.0
        )
        self.assertLess(product.qty_available, product.replenishment_target_qty)
        created = self.ReplenishmentCheck.run_replenishment_check()
        self.assertEqual(created, 1)
        self.assertEqual(self._count_replenishment_activities(product), 1)

    def test_no_activity_above_target(self):
        product = self._create_storable_product(
            "Product Enough Stock", target_qty=10.0, qty=15.0
        )
        created = self.ReplenishmentCheck.run_replenishment_check()
        self.assertEqual(created, 0)
        self.assertEqual(self._count_replenishment_activities(product), 0)

    def test_no_duplicate_open_activity(self):
        product = self._create_storable_product(
            "Product Duplicate Check", target_qty=10.0, qty=2.0
        )
        self.ReplenishmentCheck.run_replenishment_check()
        self.ReplenishmentCheck.run_replenishment_check()
        self.assertEqual(self._count_replenishment_activities(product), 1)

    def test_activity_after_done_allows_new(self):
        product = self._create_storable_product(
            "Product Done Activity", target_qty=10.0, qty=1.0
        )
        self.ReplenishmentCheck.run_replenishment_check()
        activity = self.Activity.search(
            [
                ("res_model", "=", "product.template"),
                ("res_id", "=", product.id),
                ("activity_type_id", "=", self.activity_type.id),
            ],
            limit=1,
        )
        activity.action_feedback(feedback="Test completed")
        created = self.ReplenishmentCheck.run_replenishment_check()
        self.assertEqual(created, 1)
        self.assertEqual(self._count_replenishment_activities(product), 1)
