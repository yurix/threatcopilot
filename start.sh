#!/bin/bash
source ../threatcopilot/bin/activate
gunicorn --config ./gunicorn-cfg.py --reload run:app
