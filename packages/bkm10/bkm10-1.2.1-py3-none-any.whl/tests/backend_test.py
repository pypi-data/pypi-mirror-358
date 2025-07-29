"""
Here, we test the backend functionality of the library
and see if it throws a fit.
"""

from bkm10_lib import backend, formalism

backend.set_backend("numpy")
assert np.allclose(...)

backend.set_backend("tensorflow")
assert tf.reduce_all(...)