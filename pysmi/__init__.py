# http://www.python.org/dev/peps/pep-0396/
__version__ = '0.4.0'

import sys

if sys.version_info[:2] < (3, 8):
    raise RuntimeError('PySMI requires Python 3.8 or later')
