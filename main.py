#!/usr/bin/python2
#  ____                _____                  ___   ___
# |    \ ___ ___ _ _ _| __  |___ _ _ _ ___   |_  | |   |
# |  |  |  _| .'| | | |    -| .'| | | |  _|  |  _|_| | | 
# |____/|_| |__,|_____|__|__|__,|_____|_|    |___|_|___|
# ------------ A social website for artists ------------

__version__ = '2.0'
__author__  = 'DrawRawr'

import server as server
import os,sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", 
                  default=True, help="Silence all output from DrawRawr")

# Run Server
if __name__ == "__main__": server.main()
else: print("DrawRawr isn't a module, silly.")
