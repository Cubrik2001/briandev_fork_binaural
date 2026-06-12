from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOperationTag(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tag = cls.env["stock.operation.tag"]
        cls.Wizard = cls.env["stock.operation.tag.assign.wizard"]

    def test_create_operation_tag(self):
        tag = self.Tag.create(
            {
                "name": "Picking rápido",
                "color": 1,
                "description": "Productos de picking frecuente",
                "operation_type": "picking",
            }
        )
        self.assertEqual(tag.name, "Picking rápido")
        self.assertEqual(tag.operation_type, "picking")
        self.assertEqual(tag.color, 1)

    def test_assign_tags_to_product(self):
        tag = self.Tag.create(
            {"name": "Almacenamiento frío", "operation_type": "storage"}
        )
        product = self.env["product.template"].create(
            {"name": "Producto Etiquetado", "type": "consu"}
        )
        product.operation_tag_ids = [(4, tag.id)]
        self.assertIn(tag, product.operation_tag_ids)
        product.operation_tag_ids = [(3, tag.id)]
        self.assertNotIn(tag, product.operation_tag_ids)

    def test_wizard_add_remove_tags(self):
        tag_add = self.Tag.create({"name": "Despacho express", "operation_type": "dispatch"})
        tag_remove = self.Tag.create({"name": "Temporal", "operation_type": "picking"})
        product = self.env["product.template"].create(
            {
                "name": "Producto Wizard",
                "type": "consu",
                "operation_tag_ids": [(4, tag_remove.id)],
            }
        )
        wizard = self.Wizard.create(
            {
                "product_ids": [(6, 0, product.ids)],
                "tag_ids_to_add": [(6, 0, tag_add.ids)],
                "tag_ids_to_remove": [(6, 0, tag_remove.ids)],
            }
        )
        wizard.action_apply_tags()
        self.assertIn(tag_add, product.operation_tag_ids)
        self.assertNotIn(tag_remove, product.operation_tag_ids)
