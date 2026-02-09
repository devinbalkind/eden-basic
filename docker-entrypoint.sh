#!/bin/bash
set -e

echo "========================================================================"
echo "   WARNING: SAHANA EDEN - MARKETING DEMO / SANDBOX CONFIGURATION"
echo ""
echo "   This container is configured for EVALUATION PURPOSES ONLY."
echo "   It uses Rocket+SQLite and is NOT SUITABLE FOR PRODUCTION."
echo "========================================================================"
sleep 2


# Run setup_map.py to configure GIS and fix hierarchy
# We use -S eden -M to run in the context of the app with models loaded
echo "Running Eden setup scripts..."
python web2py.py -S eden -M -R applications/eden/setup_map.py || echo "Setup script failed, but continuing..."

# Start Web2py
echo "Starting Web2py..."
exec python web2py.py -a "$WEB2PY_PASSWORD" -i 0.0.0.0 -p 8000
