"""Type-checks every ```python block of the documentation (ADR-0022).

Agents copy the examples, so they must keep compiling: each block becomes a
module of its own, checked by pyright in strict mode against the source.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = ["README.md", "AGENTS.md", "../README.md", "../AGENTS.md"]
OUT = ROOT / ".examples"


def main() -> int:
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir()
    count = 0
    for document in DOCUMENTS:
        path = ROOT / document
        if not path.exists():
            continue
        for block in re.findall(r"```python\n(.*?)```", path.read_text(), re.DOTALL):
            count += 1
            name = re.sub(r"[^A-Za-z]+", "_", document).strip("_").lower()
            (OUT / f"{name}_{count}.py").write_text(block)
    (OUT / "pyrightconfig.json").write_text(
        '{"typeCheckingMode": "strict", "pythonVersion": "3.10", '
        '"extraPaths": ["../src"], "venvPath": "..", "venv": ".venv"}'
    )
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pyright", "-p", str(OUT)], check=False
        )
    finally:
        shutil.rmtree(OUT, ignore_errors=True)
    if result.returncode != 0:
        print("A documentation example does not type-check (see above).")
        return 1
    print(f"{count} documentation examples type-check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
