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


from elina.python_interface.elina_interval_h import *

# ************************************************************************* #
# elina_coeff.h: coefficients, that are either scalars or intervals
# ************************************************************************* #


class ElinaCoeffDiscr(CtypesEnum):
    """ Enum compatible with discr field in elina_coeff_t from elina_coeff.h """

    ELINA_COEFF_SCALAR = 0
    ELINA_COEFF_INTERVAL = 1


class ElinaCoeffUnion(Union):
    """ Ctype representing the union field in elina_coeff_t from elina_coeff.h """

    _fields_ = [('scalar', ElinaScalarPtr), ('interval', ElinaIntervalPtr)]


class ElinaCoeff(Structure):
    """ ElinaCoeff ctype compatible with elina_coeff_t from elina_coeff.h """

    _fields_ = [('discr', c_uint), ('val', ElinaCoeffUnion)]


ElinaCoeffPtr = POINTER(ElinaCoeff)
