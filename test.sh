#!/bin/bash
echo "Running tests..."
python -m pytest tests/ -v --cov=app --cov-report=term-missing
