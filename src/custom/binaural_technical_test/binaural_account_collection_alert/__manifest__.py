{
    "name": "Binaural Account Collection Alert",
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "summary": "Collection risk alerts for overdue customer invoices",
    "author": "Binaural",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "views/account_collection_alert_rule_views.xml",
        "views/account_collection_alert_views.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": False,
}
