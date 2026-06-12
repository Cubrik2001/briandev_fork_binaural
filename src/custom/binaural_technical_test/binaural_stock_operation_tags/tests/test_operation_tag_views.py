from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestOperationTagViews(HttpCase):
    def test_product_operation_kanban_loads(self):
        self.authenticate("admin", "admin")
        action = self.env.ref(
            "binaural_stock_operation_tags.action_product_by_operation_tag"
        )
        response = self.url_open(
            f"/web?debug=1#action={action.id}&model=product.template&view_type=kanban"
        )
        self.assertEqual(response.status_code, 200)
