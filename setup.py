from distutils.core import setup

setup(name='fixreal',
      version='0.8',
      author="Marco Bartolini",
      author_email = "marco.bartolini@gmail.com",
      url = "https://github.com/flyingfrog81/fixreal",
      download_url = "https://github.com/flyingfrog81/fixreal/zipball/master",
      license = "gpl",
      classifiers = [
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Scientific/Engineering :: Mathematics",
          ],
      description="Defines a set of function to convert number between fixed and floating point representations",
      long_description = """
Functions to convert numbers between fixed and floating point representation as
experienced by simulink users.
Permits conversion of 8, 16 and 32 bit representation of signed and unsigned
decimal numbers, with or without binary point.

INSTALLATION
============

Package can be downloaded from the public git repo as::

    $ git clone 
    $ python setup.py install

or installed automatically via pypi::

    $ pip install fixreal


USAGE
=====

    >>> import fixreal
    >>> fixreal.real2fix(-0.9921875, fixreal.get_conv(8, 7, True))
    129.0
    >>> fixreal.real2fix(-3.96875, fixreal.get_conv(8, 5, True))
    129.0
    >>> fixreal.real2fix(-127, fixreal.get_conv(8, 0, True))
    129.0
    >>> fixreal.real2fix(1.0078125, fixreal.get_conv(8, 7, False))
    129.0
    >>> fixreal.real2fix(4.03125, fixreal.get_conv(8, 5, False))
    129.0
    >>> fixreal.real2fix(129, fixreal.get_conv(8, 0, False))
    129.0
    >>> fixreal.fix2real(0b10000001, fixreal.get_conv(8, 7, True))
    -0.9921875
    >>> fixreal.fix2real(0b10000001, fixreal.get_conv(8, 5, True))
    -3.96875
    >>> fixreal.fix2real(0b10000001, fixreal.get_conv(8, 0, True))
    -127.0
    >>> fixreal.fix2real(0b10000001, fixreal.get_conv(8, 7, False))
    1.0078125
    >>> fixreal.fix2real(0b10000001, fixreal.get_conv(8, 5, False))
    4.03125
    >>> fixreal.fix2real(0b10000001, fixreal.get_conv(8, 0, False))
    129.0
    >>> conv = fixreal.conv_from_name("fix_8_7")
      """,
      py_modules = ['fixreal'],
     )
