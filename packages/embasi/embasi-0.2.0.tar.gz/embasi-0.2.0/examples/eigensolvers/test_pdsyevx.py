import numpy as np
import os
from mpi4py import MPI
from scalapack4py import ScaLAPACK4py
from numpy.random import rand
from ctypes import CDLL, RTLD_GLOBAL, POINTER, c_int, c_double
from embasi.parallel_utils import root_print
from embasi.roothan_hall_eigensolver_scalapack import pdsyevx_from_numpy_array

libpath = os.environ['ASI_LIB_PATH']

sl = ScaLAPACK4py(CDLL(libpath, mode=RTLD_GLOBAL))

n = 7
a = np.arange(n*n).reshape((n,n))

a = (a + a.T)/2
print(a)

eigvals, eigvecs = pdsyevx_from_numpy_array(a)
root_print(f'EVALS: {eigvals}')
root_print(f'EVECS: {eigvecs}')

eigvals, eigvecs = np.linalg.eig(a)
root_print(f'EVALS: {eigvals}')
root_print(f'EVECS: {eigvecs}')
