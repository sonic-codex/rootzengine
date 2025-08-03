import sys
from pathlib import Path

# Ensure src is on PYTHONPATH for imports regardless of how pytest is run
root_dir = Path(__file__).parent.parent
src_path = root_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Also add the root directory to path for local imports
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

print(f"PYTHONPATH adjusted: {sys.path[:2]}")
