#!/usr/bin/env python3
"""
Government Budget Allocation CLI Tool

A comprehensive command-line interface for allocating government budgets
to counties using different allocation methods.

Usage:
    python cli.py --help
    python cli.py init
    python cli.py county list
    python cli.py budget create
    python cli.py budget compare --amount 1000000
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.cli.main import cli

if __name__ == '__main__':
    cli()
