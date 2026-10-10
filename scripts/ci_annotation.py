#!/usr/bin/env python3
"""CI hatasını GitHub Checks API'de okunabilir ve sırları temizlenmiş gösterir."""

import os
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(errors="replace")
text = re.sub(r"\x1b\[[0-9;]*m", "", text)
text = text.replace("\r", "\n")
for key in ("CI_ADMIN_PASSWORD", "CI_DB_PASSWORD", "GITHUB_TOKEN"):
	secret = os.environ.get(key)
	if secret:
		text = text.replace(secret, "[REDACTED]")
text = "\n".join(text.splitlines()[-30:])[-3500:]
text = text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
print("::error title=MariaDB acceptance diagnostic::" + text)
