import ast
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEFINITIONS = sorted(ROOT.glob("apps/*/*/*/doctype/*/*.json"))


@pytest.mark.parametrize("path", DEFINITIONS, ids=lambda p: p.stem)
def test_doctype_has_exported_controller_and_complete_field_order(path):
	data = json.loads(path.read_text())
	assert set(data["field_order"]) == {f["fieldname"] for f in data["fields"]}
	controller = path.with_suffix(".py")
	assert controller.exists(), str(controller)
	tree = ast.parse(controller.read_text())
	exported = {n.name for n in tree.body if isinstance(n, ast.ClassDef)}
	for node in tree.body:
		if isinstance(node, ast.ImportFrom):
			exported.update(alias.asname or alias.name for alias in node.names)
	assert data["name"].replace(" ", "").replace("-", "") in exported
