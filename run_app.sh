#!/bin/bash
cd /Users/ralitzamondal/Documents/finance-coach
export VIRTUAL_ENV=/Users/ralitzamondal/Documents/finance-coach/venv
export PATH="$VIRTUAL_ENV/bin:$PATH"
exec python3.13 app.py --port 7861
