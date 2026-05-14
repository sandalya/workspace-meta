import sys
from pathlib import Path

# Make morning_digest importable from tests/
sys.path.insert(0, str(Path(__file__).parent.parent))
