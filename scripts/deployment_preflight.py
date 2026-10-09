#!/usr/bin/env python3
"""Docker dağıtımı için sır değerlerini göstermeyen statik ön kontrol."""

import argparse
import json
import re
import sys
from pathlib import Path


def check_environment(values):
	checks = []

	def add(name, passed, message):
		checks.append({"id": name, "passed": bool(passed), "message": message})

	for key in ("CARI_DOMAIN", "CARI_SITE"):
		value = values.get(key, "")
		add(
			key,
			bool(re.fullmatch(r"[a-zA-Z0-9.-]+", value))
			and "." in value
			and not value.endswith((".invalid", ".local", "localhost")),
			"Gerçek site/alan adı gereklidir",
		)
	image = values.get("CARI_IMAGE", "")
	add(
		"image",
		(":" in image or "@sha256:" in image) and not image.endswith(":latest"),
		"Sabit sürümlü imaj gerekir; digest tercih edilir",
	)
	add(
		"erp_version",
		values.get("ERPNEXT_VERSION") == "v15.122.0",
		"Test edilen çekirdek sürümüyle aynı olmalıdır",
	)
	for key in ("DB_ROOT_PASSWORD", "INITIAL_ADMIN_PASSWORD"):
		secret = values.get(key, "")
		add(
			key,
			len(secret) >= 20
			and secret.lower() not in {"admin", "password", "changeme"}
			and "example" not in secret.lower(),
			"En az 20 karakterlik ayrı güvenli sır gerekir",
		)
	add(
		"separate_passwords",
		bool(values.get("DB_ROOT_PASSWORD"))
		and values.get("DB_ROOT_PASSWORD") != values.get("INITIAL_ADMIN_PASSWORD"),
		"DB ve uygulama sırları farklı olmalıdır",
	)
	add(
		"acme_contact",
		bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", values.get("ACME_EMAIL", ""))),
		"Sertifika bildirim adresi gerekir",
	)
	return {
		"decision": "PASS" if all(c["passed"] for c in checks) else "BLOCKED",
		"checks": checks,
		"production_acceptance": False,
	}


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--env-file", required=True)
	args = parser.parse_args()
	path = Path(args.env_file)
	if not path.is_file():
		parser.error("Env dosyası bulunamadı")
	if path.stat().st_mode & 0o077:
		print(json.dumps({"decision": "BLOCKED", "message": "Sır dosyası chmod 600/400 olmalıdır"}))
		return 1
	values = {}
	for line in path.read_text().splitlines():
		if line.strip() and not line.lstrip().startswith("#") and "=" in line:
			key, value = line.split("=", 1)
			values[key.strip()] = value.strip().strip("\"'")
	result = check_environment(values)
	print(json.dumps(result, ensure_ascii=False, indent=2))
	return 0 if result["decision"] == "PASS" else 1


if __name__ == "__main__":
	sys.exit(main())
