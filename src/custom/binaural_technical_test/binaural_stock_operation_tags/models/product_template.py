from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    operation_tag_ids = fields.Many2many(
        comodel_name="stock.operation.tag",
        relation="product_template_operation_tag_rel",
        column1="product_id",
        column2="tag_id",
        string="Etiquetas operativas",
    )
