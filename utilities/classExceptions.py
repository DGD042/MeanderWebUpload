# -*- coding: utf-8 -*-
# _____________________________________________________________________________
# _____________________________________________________________________________
#
#                       Coded by Daniel Gonzalez-Duque
#                           Last revised 2021-01-15
# _____________________________________________________________________________
# _____________________________________________________________________________
'''

The classExceptions are included in this script.
'''


# File Exceptions
class FileNotFoundError(Exception):
    pass

class FormatError(Exception):
    pass

class VariableNotFoundError(Exception):
    pass

class HUCNotFoundError(Exception):
    pass
