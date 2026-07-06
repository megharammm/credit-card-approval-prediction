import os
import sys

# Ensure the containing directory 'Source Code' is on the python import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Running Flask app on port 5000 in debug mode
    app.run(host='0.0.0.0', port=5000, debug=True)
