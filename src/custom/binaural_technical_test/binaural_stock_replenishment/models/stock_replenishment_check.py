from odoo import _, api, fields, models


class StockReplenishmentCheck(models.Model):
    _name = "stock.replenishment.check"
    _description = "Replenishment Check Service"

    name = fields.Char(default="Replenishment Check", readonly=True)

    @api.model
    def _get_activity_type(self):
        return self.env.ref(
            "binaural_stock_replenishment.mail_activity_type_replenishment",
            raise_if_not_found=False,
        )

    @api.model
    def _get_responsible_user(self, product):
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", product.company_id.id or self.env.company.id)],
            limit=1,
        )
        if warehouse and warehouse.replenishment_responsible_id:
            return warehouse.replenishment_responsible_id
        return self.env.ref("base.user_admin")

    @api.model
    def _has_open_replenishment_activity(self, product, activity_type):
        return bool(
            self.env["mail.activity"].search_count(
                [
                    ("res_model", "=", "product.template"),
                    ("res_id", "=", product.id),
                    ("activity_type_id", "=", activity_type.id),
                ]
            )
        )

    @api.model
    def _get_products_needing_replenishment(self):
        products = self.env["product.template"].search(
            [
                ("replenishment_target_qty", ">", 0),
                ("type", "=", "product"),
            ]
        )
        return products.filtered(
            lambda p: p.qty_available < p.replenishment_target_qty
        )

    @api.model
    def _create_replenishment_activity(self, product, activity_type):
        if self._has_open_replenishment_activity(product, activity_type):
            return False
        responsible = self._get_responsible_user(product)
        priority_label = dict(
            product._fields["replenish_priority"].selection
        ).get(product.replenish_priority, product.replenish_priority)
        summary = _("Reabastecimiento pendiente: %s") % product.name
        note = _(
            "El producto <b>%(product)s</b> tiene stock disponible "
            "<b>%(available)s</b> por debajo del objetivo "
            "<b>%(target)s</b>. Prioridad: <b>%(priority)s</b>."
        ) % {
            "product": product.name,
            "available": product.qty_available,
            "target": product.replenishment_target_qty,
            "priority": priority_label,
        }
        product.activity_schedule(
            activity_type_id=activity_type.id,
            summary=summary,
            note=note,
            user_id=responsible.id,
        )
        return True

    @api.model
    def run_replenishment_check(self):
        activity_type = self._get_activity_type()
        if not activity_type:
            return 0
        created = 0
        for product in self._get_products_needing_replenishment():
            if self._create_replenishment_activity(product, activity_type):
                created += 1
        return created

    @api.model
    def _cron_check_replenishment(self):
        self.run_replenishment_check()
