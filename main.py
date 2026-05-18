import asyncio
import sys
import os

# Redirect to the new interface
sys.path.append(os.getcwd())
from interface.cli import run_chat

if __name__ == "__main__":
    try:
        asyncio.run(run_chat())
    except (EOFError, KeyboardInterrupt):
        pass
