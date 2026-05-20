import asyncio
import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from interface.cli import run_chat

if __name__ == "__main__":
    try:
        asyncio.run(run_chat())
    except (EOFError, KeyboardInterrupt):
        pass
