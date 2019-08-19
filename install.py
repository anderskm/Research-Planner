#!/usr/bin/env python
import subprocess
import sys

def install():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print('\nInstallation completed')
    except Exception as ex:
        print('\nAn error occured while installing the requied packages:')
        print(ex)
    finally:
        input("\nPress Enter to continue...")

# Example
if __name__ == '__main__':
    install()