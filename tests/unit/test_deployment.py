import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("preflight", ROOT / "scripts/deployment_preflight.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_example_environment_is_not_production_ready():
	assert module.check_environment({})["decision"] == "BLOCKED"


def test_preflight_redacts_all_password_values():
	values = {
		"CARI_DOMAIN": "erp.company.test",
		"CARI_SITE": "erp.company.test",
		"CARI_IMAGE": "cari/erpnext:0.1.0",
		"ERPNEXT_VERSION": "v15.122.0",
		"DB_ROOT_PASSWORD": "A" * 32,
		"INITIAL_ADMIN_PASSWORD": "B" * 32,
		"ACME_EMAIL": "ops@company.test",
	}
	result = module.check_environment(values)
	assert result["decision"] == "PASS"
	assert values["DB_ROOT_PASSWORD"] not in str(result)
	assert values["INITIAL_ADMIN_PASSWORD"] not in str(result)
	assert result["production_acceptance"] is False


def test_only_reverse_proxy_exposes_ports_and_application_has_egress():
	data = yaml.safe_load((ROOT / "deploy/compose.yml").read_text())
	assert {name for name, service in data["services"].items() if service.get("ports")} == {"caddy"}
	assert data["networks"]["private"]["internal"] is True
	for name in ["backend", "queue-short", "queue-long", "scheduler"]:
		assert "egress" in data["services"][name]["networks"]
	assert "INITIAL_ADMIN_PASSWORD" not in str(data["services"]["backend"]["environment"])
