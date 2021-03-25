#!/usr/bin/python

import sys
from game import main_02 as main

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        main.run()
    else:
        test = None
        import_str = sys.argv[1][:-3].replace("/", ".").replace("\\", ".").lstrip("\\./")
        exec('import {} as test'.format(import_str))
        test.run()
