from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py
from setuptools import find_packages
import numpy
import os

# Function to get the appropriate compile flags based on file extension
def get_compile_flags(file_name):
    if file_name.endswith('.c'):
        return ['-std=c11']  # C files should be compiled with C standard
    elif file_name.endswith('.cpp'):
        return ['-std=c++11']  # C++ files should be compiled with C++ standard
    return []

# Define the SWIG extension
swig_sources = [
    'nfdrs4py/nfdrs4.i',
    'lib/NFDRS4/src/deadfuelmoisture.cpp', 'lib/NFDRS4/src/livefuelmoisture.cpp',
    'lib/NFDRS4/src/dfmcalcstate.cpp', 'lib/NFDRS4/src/lfmcalcstate.cpp',
    'lib/NFDRS4/src/nfdrs4calcstate.cpp', 'lib/NFDRS4/src/nfdrs4.cpp',
    'lib/NFDRS4/src/CNFDRSParams.cpp', 'lib/utctime/src/utctime.cpp',
    'lib/time64/src/time64.c'  # This is the C file causing the issue
]

# Apply the appropriate compile flags to each source file
extra_compile_args = []
for source in swig_sources:
    extra_compile_args.extend(get_compile_flags(source))

# Define the SWIG extension with proper flags
swig_extension = Extension(
    name='nfdrs4py._nfdrs4_bindings',  # Name of the Python package
    sources=swig_sources,
    swig_opts=['-c++'],  # SWIG options
    language='c++',  # The main extension is in C++
    include_dirs=['lib/NFDRS4/include', 'lib/time64/include', 'lib/utctime/include', numpy.get_include()],
    extra_compile_args=extra_compile_args,  # Add our conditional compile args here
    extra_link_args=[],  # Additional linker options
)

class BuildPy(build_py):
    def run(self):
        self.run_command('build_ext')
        super(BuildPy, self).run()

setup(
    name='nfdrs4py',
    version='0.2.0',
    description='Python interface to NFDRS',
    url='https://github.com/j-tenny/NFDRS4py',
    ext_modules=[swig_extension],
    cmdclass={
        'build_py': BuildPy,
    },
    packages=find_packages(),
)
