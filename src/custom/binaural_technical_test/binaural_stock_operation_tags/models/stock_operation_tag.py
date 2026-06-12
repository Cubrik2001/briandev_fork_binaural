from odoo import fields, models


class StockOperationTag(models.Model):
    _name = "stock.operation.tag"
    _description = "Stock Operation Tag"
    _order = "name"

    name = fields.Char(string="Nombre", required=True)
    color = fields.Integer(string="Color")
    description = fields.Text(string="Descripción")
    operation_type = fields.Selection(
        selection=[
            ("picking", "Picking"),
            ("storage", "Almacenamiento"),
            ("dispatch", "Despacho"),
        ],
        string="Tipo de operación",
        required=True,
        default="picking",
    )
    product_count = fields.Integer(
        string="Cantidad de productos",
        compute="_compute_product_count",
    )

    def _compute_product_count(self):
        for tag in self:
            tag.product_count = len(tag.product_ids)

    product_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_operation_tag_rel",
        column1="tag_id",
        column2="product_id",
        string="Productos",
    )
