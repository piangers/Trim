# -*- coding: utf-8 -*-



# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
   
    #
    from trim import Trim
    return Trim(iface)
