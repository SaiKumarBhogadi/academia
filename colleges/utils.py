import json
import os

# Calculate BASE_DIR relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load states and districts
with open(os.path.join(BASE_DIR, 'data', 'indian_states_districts.json'), 'r') as f:
    STATES_DISTRICTS = json.load(f)