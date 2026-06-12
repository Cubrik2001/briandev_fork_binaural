{
    "name": "Binaural Stock Replenishment Priority",
    "version": "17.0.1.0.0",
    "category": "Inventory",
    "summary": "Replenishment priority rules with automatic activities",
    "author": "Binaural",
    "license": "LGPL-3",
    "depends": ["stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_activity_type_data.xml",
        "data/ir_cron_data.xml",
        "views/stock_warehouse_views.xml",
        "views/product_template_views.xml",
        "views/stock_replenishment_check_views.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": False,
}
