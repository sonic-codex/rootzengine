# Automatically add src directory to sys.path so rootzengine package is discoverable
import sys
import os
project_root = os.path.dirname(__file__)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
