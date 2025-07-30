from setuptools import setup, Extension
import sys

import os
import subprocess

def make_libdars(plat_name, lib_name):
    '''
    Builds the shared library for the specified platform.
    Args:
        plat_name (str): The platform name (e.g., 'win32', 'win_amd64').
        lib_name (str): The name of the library to be built.
    '''
    # Effect of this function is to build the shared library and install it to the package directory dvars/dars
    # Equivalent commands for building and installing the library:
	# make -C libsrc PLAT=win32 && make -C libsrc install PLAT=win32
	# make -C libsrc PLAT=win_amd64 && make -C libsrc install PLAT=win_amd64

    # Ensure the Makefile exists in the libsrc directory
    makefile_path = 'libsrc/Makefile'
    if not os.path.exists(makefile_path):
        raise FileNotFoundError("Makefile not found at "+makefile_path+". Please ensure it exists in the libsrc directory.")
    # Build the shared library
    try:
        subprocess.run(['make', '-C', 'libsrc', 'PLAT='+plat_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during building the shared library: {e}")
        print("Make sure you have 'make' installed and the Makefile is correctly configured.")
        raise
    # Check if the shared library was built successfully
    lib_path = os.path.join('libsrc', lib_name)
    if not os.path.exists(lib_path):
        raise FileNotFoundError("Shared library not found at "+lib_path+". Please ensure it was built successfully.")
    # Install the shared library to the package directory dvars/dars
    try:
        subprocess.run(['make', '-C', 'libsrc', 'install', 'PLAT='+plat_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during installing the shared library: {e}")
        print("Make sure you have 'make' installed and the Makefile is correctly configured.")
        raise

# setup.py for dvars package
plat_name = ''
for i in range(len(sys.argv)):
    if sys.argv[i].startswith('--plat-name'):
        plat_name = sys.argv[i].split('=')[1] if '=' in sys.argv[i] else sys.argv[i + 1]
        print(f"Found platform name: {plat_name}")
        break

if sys.platform=='linux' and plat_name in ['win-amd64','win_amd64','win32']:
    # cross-build
    lib_extension = '.pyd' # Windows shared library extension
    lib_name = 'libdars_'+plat_name+lib_extension
    print(f"Library name: {lib_name}")
    # Build the shared library using the Makefile in libsrc
    make_libdars(plat_name, lib_name)
    # Copy the pre-built library to the package data
    setup(
        package_data={
            'dvars.dars': [lib_name],
            },
        )
else:
    # native build
    setup(
        ext_modules=[
            Extension(
                name='libdars',
                sources=['libsrc/dars.c', 'libsrc/roesset_quake.c'],
                )
            ],
        #package_data={
        #    'dvars.dars': ['libdars*.so', 'libdars*.pyd', 'libdars*.dll'],
        #    },
        ext_package='dvars.dars',
        )
