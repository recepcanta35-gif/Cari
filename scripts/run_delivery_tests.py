#!/usr/bin/env python3
"""T2/T3 kabulünü demo MariaDB sitesinde çalıştırır; testler rollback edilir."""

import argparse
import json
import os
import sys
import unittest
from pathlib import Path


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--bench", required=True)
	parser.add_argument("--site", required=True)
	parser.add_argument("--report")
	args = parser.parse_args()
	report_path = Path(args.report).resolve() if args.report else None
	os.chdir(Path(args.bench).resolve() / "sites")
	import frappe

	frappe.init(site=args.site, sites_path=".")
	frappe.connect()
	try:
		if not frappe.conf.get("developer_mode"):
			parser.error("Test verisi yalnız demo/developer sitesinde kullanılabilir")
		suite = unittest.defaultTestLoader.loadTestsFromName("cari_custom.tests.test_delivery")
		suite.addTests(
			unittest.defaultTestLoader.loadTestsFromName("cari_custom.tests.test_business.BusinessTests")
		)
		result = unittest.TextTestRunner(verbosity=2).run(suite)
		evidence = {
			"suite": "identity-field-operations",
			"status": "PASS" if result.wasSuccessful() else "FAIL",
			"tests_run": result.testsRun,
			"failures": len(result.failures),
			"errors": len(result.errors),
			"database": frappe.conf.get("db_type", "mariadb"),
			"production_acceptance": False,
		}
		if report_path:
			report_path.write_text(json.dumps(evidence, indent=2) + "\n")
		return 0 if result.wasSuccessful() else 1
	finally:
		frappe.db.rollback()
		frappe.destroy()


if __name__ == "__main__":
	sys.exit(main())
