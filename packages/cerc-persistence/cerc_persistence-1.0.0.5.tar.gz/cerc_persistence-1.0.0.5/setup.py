import glob
import pathlib
from distutils.util import convert_path

from setuptools import setup

with pathlib.Path('requirements.txt').open() as r:
  install_requires = [
    str(requirement).replace('\n', '')
    for requirement
    in r.readlines()
  ]
install_requires.append('setuptools')

main_ns = {}
version = convert_path('cerc_persistence/version.py')
with open(version) as f:
  exec(f.read(), main_ns)

setup(
  name='cerc-persistence',
  version=main_ns['__version__'],
  description="CERC Persistence consist of a set of classes to store and retrieve Cerc Hub cities and results",
  long_description="CERC Persistence consist of a set of classes to store and retrieve Cerc Hub cities and results.\n\n"
                   "Developed at Concordia university in Canada as part of the research group from the Next Generation "
                   "Cities Institute, our aim among others is to provide a comprehensive set of tools to help "
                   "researchers and urban developers to make decisions to improve the livability and efficiency of our "
                   "cities, cerc persistence will store the simulation results and city information to make those "
                   "available for other researchers.",
  classifiers=[
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
  ],
  include_package_data=True,
  packages=[
    'cerc_persistence',
    'cerc_persistence.models',
    'cerc_persistence.repositories',
    'cerc_persistence.types'
  ],
  setup_requires=install_requires,
  install_requires=install_requires,
  data_files=[
    ('cerc_persistence', glob.glob('requirements.txt')),
  ],
)
