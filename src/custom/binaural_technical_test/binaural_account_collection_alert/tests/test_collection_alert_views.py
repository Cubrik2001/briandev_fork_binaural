from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCollectionAlertViews(HttpCase):
    def test_collection_alert_kanban_loads(self):
        self.authenticate("admin", "admin")
        action = self.env.ref(
            "binaural_account_collection_alert.action_account_collection_alert"
        )
        response = self.url_open(
            f"/web?debug=1#action={action.id}&model=account.collection.alert&view_type=kanban"
        )
        self.assertEqual(response.status_code, 200)
