#!/usr/bin/env python3
"""
SnapTidy CLI - Command line interface for organizing and deduplicating files.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.cli import main

if __name__ == "__main__":
    sys.exit(main())
