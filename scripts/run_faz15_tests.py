#!/usr/bin/env python3
"""Demo sitesindeki testleri bench Python'u ile, gerçek exit code ile çalıştırır."""

import argparse
import json
import os
import sys
import unittest
from pathlib import Path


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--bench", default="/home/user/frappe-bench")
	parser.add_argument("--site", default="cari.local")
	parser.add_argument("--report", help="İsteğe bağlı JSON kabul raporu dosyası")
	args = parser.parse_args()
	report_path = Path(args.report).resolve() if args.report else None
	os.chdir(Path(args.bench).resolve() / "sites")
	import frappe

	frappe.init(site=args.site, sites_path=".")
	frappe.connect()
	try:
		if not frappe.conf.get("developer_mode"):
			parser.error("Bu testler yalnızca developer_mode=1 olan demo sitesinde çalışır.")
		suite = unittest.defaultTestLoader.loadTestsFromName("cari_custom.tests.test_faz15")
		result = unittest.TextTestRunner(verbosity=2).run(suite)
		if not result.wasSuccessful():
			return 1
		from cari_custom.sample_validation import verify

		report = verify()
		report["regression_tests"] = {
			"run": result.testsRun,
			"failures": len(result.failures),
			"errors": len(result.errors),
		}
		if report_path:
			report_path.parent.mkdir(parents=True, exist_ok=True)
			report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
		print(f"FAZ15 PASS: {report['checks_passed']} kabul kontrolü; {result.testsRun} regresyon testi.")
		return 0
	finally:
		frappe.db.rollback()
		frappe.destroy()


if __name__ == "__main__":
	sys.exit(main())
