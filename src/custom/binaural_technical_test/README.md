# Binaural Technical Test - Odoo 17

Three custom modules for the Binaural technical assessment.

## Modules

| Module | Description |
|--------|-------------|
| `binaural_stock_replenishment` | Replenishment priority, target stock, automatic activities |
| `binaural_stock_operation_tags` | Operational tags and quick assignment wizard |
| `binaural_account_collection_alert` | Collection risk rules and alert board |

## Install

```bash
./odoo update -d <database> -m binaural_stock_replenishment,binaural_stock_operation_tags,binaural_account_collection_alert
```

## Run tests (--test-enable)

```bash
python3 src/custom/binaural_technical_test/run_tests.py --database testing --install
```

Or manually:

```bash
docker exec -u odoo proj odoo \
  --test-enable \
  --test-tags /binaural_stock_replenishment,/binaural_stock_operation_tags,/binaural_account_collection_alert \
  -d testing \
  -i binaural_stock_replenishment,binaural_stock_operation_tags,binaural_account_collection_alert \
  --without-demo=False \
  --stop-after-init \
  --workers 0 \
  -p 9999 \
  -c /home/odoo/.config/odoo.conf \
  --log-level=test
```

## Manual verification

- **Inventory > Operations > Pending replenishment** — products below target stock grouped by priority
- **Inventory > Products by operation tag** — kanban grouped by tags
- **Accounting > Customers > Collection alerts** — kanban grouped by risk level
- **Accounting > Configuration > Collection alert rules** — configure rules and recompute alerts
