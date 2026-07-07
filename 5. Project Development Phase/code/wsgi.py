import os
import sys

# Ensure Python looks in the current directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

