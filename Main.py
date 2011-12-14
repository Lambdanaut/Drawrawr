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

# Loading engines
engines = {}
enginesDirectory = os.listdir(os.path.join(sys.path[0], 'system', 'engines'))

for engine in enginesDirectory:
  engineParts = os.path.splitext(engine)
  
  if engineParts[1] is '.py' and engineParts[0] is not '__init__':
    engines[engineParts[0]] = __import__("system.engines." + engineParts[0])

# Run Server
if __name__ == "__main__": server.app.run(host='0.0.0.0',debug=True)
else: print("DrawRawr isn't a module, silly.")
