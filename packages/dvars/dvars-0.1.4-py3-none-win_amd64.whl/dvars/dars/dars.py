import ctypes
import numpy as np
from ctypes import c_int, c_float, c_double, POINTER

def dars(data: np.ndarray, sampling_rate: float,
               nfreq=40, freq1=1.0, freq2=50.0, damp=0.05) -> (np.ndarray, np.ndarray):
    """
    Perform the PSA analysis using a c subroutines dars and rdcalcdp from
    the shared library dars.so. 

    Parameters
    ----------
    damp=0.05 : float
        The harmonic oscillator damping.
    nfreq=40 : int
        The number of frequencies.
    freq1=1.0 : float
        The first frequency.
    freq2=50.0 : float
        The last frequency.

    Input data
    ----------
    data : np.ndarray
        The input accelerogram.
    sampling_rate : float
        The sampling rate.

    Returns
    -------
    freq: np.ndarray
        The frequency array.
    srd: np.ndarray
        The relative displacement response spectrum.
    saa: np.ndarray
        The absolute accelerarion response spectrum.
    """
    # Check the length of data
    if len(data) == 0:
        raise ValueError("Data array cannot be empty.")
    # Check the sample rate
    if sampling_rate <= 0:
        raise ValueError("Sample rate must be positive.")
    # Check the damp value
    if damp < 0:
        raise ValueError("Damping value must be non-negative.")
    if damp > 1:
        raise ValueError("Damping value must be less than 1.")
    # Calculate the time step
    dt = 1 / sampling_rate
    # Calculate the number of samples
    n_samples = len(data)
    n_freq = nfreq
    from . import libdars # from the same directory
    # Get the function psa from the shared library
    psa = libdars.dars
    # Set the argument types for the C function
    # void psa(float damp, int na, float dt, float a[],
    #          int nf, double freq1, double freq2, double freq[], float sa[]);
    psa.argtypes = [c_float, c_int, c_float, POINTER(c_float),
                    c_int, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    # Set the return type of the function
    psa.restype = None
    
    # Convert the data to a ctypes array
    data_array = (c_float * len(data))(*data)

    # Allocate memory for the output
    freq_array = (c_double * nfreq)()
    srd_array = (c_double * nfreq)()
    saa_array = (c_double * nfreq)()

    # Call the C function psa
    psa(c_float(damp), n_samples, dt, data_array, n_freq, freq1, freq2, freq_array, srd_array, saa_array)

    # Convert the result to numpy arrays
    freq = np.ctypeslib.as_array(freq_array, shape=(n_freq,))
    srd = np.ctypeslib.as_array(srd_array, shape=(n_freq,))
    saa = np.ctypeslib.as_array(saa_array, shape=(n_freq,))
    return freq,srd,saa

