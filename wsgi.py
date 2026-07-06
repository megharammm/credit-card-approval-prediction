import os
import sys

# Ensure Python looks into 'Source Code' directory for python files/packages
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Source Code'))

from app import create_app

app = create_app()
