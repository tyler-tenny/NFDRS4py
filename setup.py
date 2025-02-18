from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py
from setuptools import find_packages
import numpy

# Define the SWIG extension
swig_extension = Extension(
    name='nfdrs4py._nfdrs4_bindings',  # Name of the Python package
    sources=['nfdrs4py/nfdrs4.i', 'lib/NFDRS4/src/deadfuelmoisture.cpp',  'lib/NFDRS4/src/livefuelmoisture.cpp',
             'lib/NFDRS4/src/dfmcalcstate.cpp', 'lib/NFDRS4/src/lfmcalcstate.cpp','lib/NFDRS4/src/nfdrs4calcstate.cpp',
             'lib/NFDRS4/src/nfdrs4.cpp', 'lib/NFDRS4/src/CNFDRSParams.cpp', 'lib/utctime/src/utctime.cpp', 'lib/time64/src/time64.c'],
    swig_opts=['-c++'],  # SWIG options
    language='c++',
    include_dirs=['lib/NFDRS4/include','lib/time64/include','lib/utctime/include',numpy.get_include()],  # C:/Users/john1/miniforge3/include/
    extra_compile_args=[],  # Additional compiler options
    extra_link_args=[],  # Additional linker options
)

class BuildPy(build_py):
    def run(self):
        self.run_command('build_ext')
        super(build_py, self).run()

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
    #package_dir={'nfdrs4py': 'nfdrs4py'}
)
