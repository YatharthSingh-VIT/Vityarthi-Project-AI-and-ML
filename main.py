import sys
import os

# Ensure local modules are importable when running from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import AlgoVizApp


def main():
    viz = AlgoVizApp()
    viz.run()


if __name__ == '__main__':
    main()
