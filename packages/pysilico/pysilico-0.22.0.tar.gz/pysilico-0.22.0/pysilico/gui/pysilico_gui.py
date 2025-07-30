#!/usr/bin/env python
import sys
from pysilico.gui.camera_control_gui import Runner


__version__ = "$Id: tipico_mirror_controller_1.py 31 2018-01-27 10:47:29Z lbusoni $"



def main():
    runner= Runner()
    print("%s" % sys.argv)
    sys.exit(runner.run(sys.argv[1:]))


if __name__ == '__main__':
    main()
