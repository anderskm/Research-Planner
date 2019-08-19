#!/usr/bin/env python
import subprocess
import sys

def install():
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r' ,'requirements.txt'])

# Example
if __name__ == '__main__':
    install()