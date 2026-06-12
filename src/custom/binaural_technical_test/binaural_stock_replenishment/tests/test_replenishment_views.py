from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestReplenishmentViews(HttpCase):
    def test_pending_replenishment_list_loads(self):
        self.authenticate("admin", "admin")
        action = self.env.ref(
            "binaural_stock_replenishment.action_pending_replenishment_products"
        )
        response = self.url_open(
            f"/web?debug=1#action={action.id}&model=product.template&view_type=list"
        )
        self.assertEqual(response.status_code, 200)
