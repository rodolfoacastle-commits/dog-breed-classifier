#!/usr/bin/env bash
# Start the Dog Breed Classifier server (uses port 5001 to avoid conflict with AirPlay on 5000)
cd "$(dirname "$0")"
./venv/bin/python -m flask run --host=127.0.0.1 --port=5001
