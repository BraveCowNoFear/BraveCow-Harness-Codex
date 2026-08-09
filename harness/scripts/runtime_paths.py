from __future__ import annotations

import os
from pathlib import Path


HOME = Path.home()
BRAVECOW_HOME = Path(os.environ.get("BRAVECOW_HOME", HOME / ".bravecow"))
HARNESS_HOME = Path(os.environ.get("BRAVECOW_HARNESS_HOME", BRAVECOW_HOME / "harness"))
MEMORY_HOME = Path(os.environ.get("BRAVECOW_MEMORY_HOME", BRAVECOW_HOME / "memories"))

CODEX_HOME = Path(os.environ.get("CODEX_HOME", HOME / ".codex"))
ZCODE_HOME = Path(os.environ.get("ZCODE_HOME", HOME / ".zcode"))
AGENTS_HOME = Path(os.environ.get("AGENTS_HOME", HOME / ".agents"))
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", HOME / ".openclaw"))
SHARED_SKILLS_HOME = Path(os.environ.get("SHARED_SKILLS_HOME", AGENTS_HOME / "skills"))

RUNTIME_SKILL_ROOTS = {
    "shared": SHARED_SKILLS_HOME,
    "codex": CODEX_HOME / "skills",
    "zcode": ZCODE_HOME / "skills",
    "openclaw": OPENCLAW_HOME / "skills",
}
