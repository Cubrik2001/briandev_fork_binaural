{
    "name": "Binaural Stock Operation Tags",
    "version": "17.0.1.0.0",
    "category": "Inventory",
    "summary": "Operational tags for product classification in inventory",
    "author": "Binaural",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_operation_tag_views.xml",
        "views/product_template_views.xml",
        "wizard/stock_operation_tag_assign_wizard_views.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": False,
}
