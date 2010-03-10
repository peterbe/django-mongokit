#!/bin/bash
coverage run tests.py
coverage report __init__.py document.py mongodb/__init__.py shortcut.py mongodb/base.py
coverage html __init__.py document.py mongodb/__init__.py shortcut.py mongodb/base.py
ls htmlcov/index.html