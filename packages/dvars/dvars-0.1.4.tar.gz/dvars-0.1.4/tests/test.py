import numpy as np
from .dars import dars

# Test the function dars
if __name__ == "__main__":
    # Test the function
    # Load the shared library
    loadlib_cPARS()
    print(lib)
    # Test data
    data = np.random.rand(1000)
    sampling_rate = 100.0
    freq,srd,saa = cPARS(data, sampling_rate, damp=0.05)
    print("Frequency array:")
    print(freq)
    print("Pseudo spectral amplitudes array:")
    print(srd*(freq*2*np.pi)**2)
    print(saa)


