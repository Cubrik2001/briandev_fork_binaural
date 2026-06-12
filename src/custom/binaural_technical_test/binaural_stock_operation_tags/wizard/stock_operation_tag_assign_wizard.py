from odoo import api, fields, models


class StockOperationTagAssignWizard(models.TransientModel):
    _name = "stock.operation.tag.assign.wizard"
    _description = "Assign Operation Tags Wizard"

    product_ids = fields.Many2many(
        comodel_name="product.template",
        string="Productos",
        required=True,
    )
    tag_ids_to_add = fields.Many2many(
        comodel_name="stock.operation.tag",
        relation="stock_operation_tag_wizard_add_rel",
        string="Etiquetas a agregar",
    )
    tag_ids_to_remove = fields.Many2many(
        comodel_name="stock.operation.tag",
        relation="stock_operation_tag_wizard_remove_rel",
        string="Etiquetas a remover",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if (
            self.env.context.get("active_model") == "product.template"
            and self.env.context.get("active_ids")
        ):
            res["product_ids"] = [(6, 0, self.env.context["active_ids"])]
        return res

    def action_apply_tags(self):
        self.ensure_one()
        for product in self.product_ids:
            commands = []
            if self.tag_ids_to_add:
                commands.extend((4, tag.id) for tag in self.tag_ids_to_add)
            if self.tag_ids_to_remove:
                commands.extend((3, tag.id) for tag in self.tag_ids_to_remove)
            if commands:
                product.write({"operation_tag_ids": commands})
        return {"type": "ir.actions.act_window_close"}
