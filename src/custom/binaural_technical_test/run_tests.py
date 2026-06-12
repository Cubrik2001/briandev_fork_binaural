#!/usr/bin/env python3
"""Run unit tests for Binaural technical test modules."""

import os
import subprocess
import sys

import click
from dotenv import load_dotenv


MODULES = [
    "binaural_stock_replenishment",
    "binaural_stock_operation_tags",
    "binaural_account_collection_alert",
]


@click.command()
@click.option("--database", default="testing", help="Database name for tests.")
@click.option("--install", is_flag=True, help="Install modules (-i) instead of update (-u).")
def run_command(database, install):
    load_dotenv()
    project_name = os.getenv("PROJECT_NAME", "proj")
    modules_str = ",".join(MODULES)
    test_tags = "/" + ",/".join(MODULES)
    install_flag = "-i" if install else "-u"
    command = (
        f"docker exec -u odoo {project_name} odoo "
        f"--test-enable "
        f"--test-tags {test_tags} "
        f"-d {database} "
        f"{install_flag} {modules_str} "
        f"--without-demo=False "
        f"--stop-after-init "
        f"--workers 0 "
        f"-p 9999 "
        f"-c /home/odoo/.config/odoo.conf "
        f"--log-level=test"
    )
    click.echo(f"Running: {command}")
    sys.exit(subprocess.call(command, shell=True))


if __name__ == "__main__":
    run_command()
