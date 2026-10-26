#!/usr/bin/env python3
import sys
import os
import subprocess

# Set UTF-8 encoding for the subprocess environment
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
env['PYTHONUTF8'] = '1'

# Run mcadb with proper encoding
result = subprocess.run(['uvx', 'mcadb'] + sys.argv[1:], env=env, encoding='utf-8')
sys.exit(result.returncode)
