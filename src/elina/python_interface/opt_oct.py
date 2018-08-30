#
#
#  This source file is part of ELINA (ETH LIbrary for Numerical Analysis).
#  ELINA is Copyright © 2018 Department of Computer Science, ETH Zurich
#  This software is distributed under GNU Lesser General Public License Version 3.0.
#  For more information, see the ELINA project website at:
#  http://elina.ethz.ch
#
#  THE SOFTWARE IS PROVIDED "AS-IS" WITHOUT ANY WARRANTY OF ANY KIND, EITHER
#  EXPRESS, IMPLIED OR STATUTORY, INCLUDING BUT NOT LIMITED TO ANY WARRANTY
#  THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS OR BE ERROR-FREE AND ANY
#  IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
#  TITLE, OR NON-INFRINGEMENT.  IN NO EVENT SHALL ETH ZURICH BE LIABLE FOR ANY     
#  DAMAGES, INCLUDING BUT NOT LIMITED TO DIRECT, INDIRECT,
#  SPECIAL OR CONSEQUENTIAL DAMAGES, ARISING OUT OF, RESULTING FROM, OR IN
#  ANY WAY CONNECTED WITH THIS SOFTWARE (WHETHER OR NOT BASED UPON WARRANTY,
#  CONTRACT, TORT OR OTHERWISE).
#
#


from elina.python_interface.opt_oct_imports import *
from elina.python_interface.elina_manager_h import *

# ====================================================================== #
# Basics
# ====================================================================== #

def opt_oct_manager_alloc():
    """
    Allocates an ElinaManager.

    Returns
    -------
    man : ElinaManagerPtr
        Pointer to the newly allocated ElinaManager.

    """

    man = None
    try:
        opt_oct_manager_alloc_c = opt_oct_api.opt_oct_manager_alloc
        opt_oct_manager_alloc_c.restype = ElinaManagerPtr
        opt_oct_manager_alloc_c.argtypes = None
        man = opt_oct_manager_alloc_c()
    except:
        print('Problem with loading/calling "opt_oct_manager_alloc" from "liboptoct.so"')

    return man
