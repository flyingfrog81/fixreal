# coding=utf-8

#
#
#    Copyright (C) 2012  Marco Bartolini, marco.bartolini@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Functions to convert numbers between fixed and floating point representation as
experienced by simulink users.
Permits conversion of 8, 16 and 32 bit representation of signed and unsigned
decimal numbers, with or without binary point.

INSTALLATION
============

Package can be downloaded from the public git repo as::

    $ git clone git://github.com/flyingfrog81/fixreal.git
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

@author: Marco Bartolini
@contact: marco.bartolini@gmail.com
@version: 0.8
"""

import struct
import re

class ConversionError(BaseException):
    """
    Raised when conversion types are conflicting  
    """
    pass

def get_conv(bits, bin_point, signed=False, scaling=1.0):
    """
    Creates a I{conversion structure} implented as a dictionary containing all parameters
    needed to switch between number representations.
    @param bits: the number of bits
    @param bin_point: binary point position
    @param signed: True if Fix, False if UFix
    @param scaling: optional scaling to be applied after the conversion
    @return: a conversion structure that can be applied in both directions of
    conversion for the given specs.
    """
    conversion_t = {}
    conversion_t["bits"] = bits
    conversion_t["bin_point"] = bin_point
    conversion_t["signed"] = signed
    conversion_t["scaling"] = scaling
    conversion_t["dec_step"] = 1.0 / (2 ** bin_point)
    #dec_max = dec_mask * dec_step
    conversion_t["dec_mask"] = sum([2 ** i for i in range(bin_point)])
    if bits == 8:
        conversion_t["fmt"] = "B"
    elif bits == 16:
        conversion_t["fmt"] = "H"
    elif bits == 32:
        conversion_t["fmt"] = "I"
    else:
        raise ConversionError("numer of bits not supported: " + str(bits))
    if signed:
        _get_signed_params(conversion_t)
    else:
        _get_unsigned_params(conversion_t)
    return conversion_t

def conv_from_name(name):
    """
    Understand simulink syntax for fixed types and returns the proper
    conversion structure. 
    @param name: the type name as in simulin (i.e. UFix_8_7 ... )
    @raise ConversionError: When cannot decode the string
    """
    _match = re.match(r"^(?P<signed>u?fix)_(?P<bits>\d+)_(?P<binary>\d+)", 
            name, flags = re.I)
    if not _match:
        raise ConversionError("Cannot interpret name: " + name)
    params = _match.groupdict()
    if params['signed'] == 'fix':
        signed = True
    else:
        signed = False
    bits = int(params['bits'])
    binary = int(params['binary'])
    return get_conv(bits, binary, signed)

def _get_unsigned_params(conv):
    """
    Fill the sign-dependent params of the conv structure in case of unsigned 
    conversion
    @param conv: the structure to be filled
    """
    conv["sign_mask"] = 0
    conv["int_min"] = 0
    conv["int_mask"] = sum([2 ** i for i in range(conv["bin_point"], 
        conv["bits"])])
    conv["int_max"] = sum([2 ** i for i in range(conv["bits"] -
        conv["bin_point"])])

def _get_signed_params(conv):
    """
    Fill the sign-dependent params of the conv structure in case of signed 
    conversion
    @param conv: the structure to be filled
    """
    conv["sign_mask"] = 2 ** (conv["bits"] - 1)
    conv["int_min"] = -1 * (2 ** (conv["bits"] - 1 - conv["bin_point"]))
    conv["int_mask"] = sum([2 ** i 
        for i in range(conv["bin_point"], conv["bits"] - 1)])
    conv["int_max"] = sum([2 ** i for i in range(conv["bits"] -
        conv["bin_point"] - 1)])

def fix2real(uval, conv):
    """
    Convert a 32 bit unsigned int register into the value it represents in its Fixed arithmetic form.
    @param uval: the numeric unsigned value in simulink representation
    @param conv: conv structure with conversion specs as generated by I{get_conv}
    @return: the real number represented by the Fixed arithmetic defined in conv
    @todo: Better error detection and management of unsupported operations and arguments
    """
    res = 0
    int_val =  ((uval & conv["int_mask"]) >> conv["bin_point"])
    dec_val = conv["dec_step"] * (uval & conv["dec_mask"])
    if conv["signed"] and (uval & conv["sign_mask"] > 0):
        res = conv["int_min"] + int_val + dec_val
    else: 
        res = int_val + dec_val
    return (res / conv["scaling"])

def bin2real(binary_string, conv, endianness="@"):
    """
    Converts a binary string representing a number to its Fixed arithmetic representation
    @param binary_string: binary number in simulink representation
    @param conv: conv structure containing conversion specs
    @param endianness: optionally specify bytes endianness for unpacking
    @return: the real number represented
    @attention: The length of the binary string must match with the data type defined
                in the conv structure, otherwise proper erros will be thrown by B{struct} 
                module.
    """
    data = struct.unpack(endianness + conv["fmt"], binary_string)[0]
    return fix2real(data, conv)

def stream2real(binary_stream, conv, endianness="@"):
    """
    Converts a binary stream into a sequence of real numbers
    @param binary_stream: a binary string representing a sequence of numbers
    @param conv: conv structure containing conversion specs
    @param endianness: optionally specify bytes endianness for unpacking
    @return: the list of real data represented
    """
    size = len(binary_stream) // (conv["bits"] // 8)
    fmt = endianness + str(size) + conv["fmt"]
    data = struct.unpack(fmt, binary_stream)
    data = [fix2real(d, conv) for d in data]
    return data

def real2fix(real, conv):
    """
    Convert a real number to its fixed representation so 
    that it can be written into a 32 bit register.
    @param real: the real number to be converted into fixed representation
    @param conv: conv structre with conversion specs
    @return: the fixed representation of the real number 
    @raise ConverisonError: if conv structre can't handle the real number.
    @todo: Better error detection and management of unsupported 
    operations and arguments
    """
    if not conv["signed"] and real < 0:
        raise ConversionError("cannot convert " + 
                str(real) + " to unsigned representation")
    if real < 0:
        sign = 1
        real = real - conv["int_min"] 
    else:
        sign = 0
    int_val, dec_val = divmod(abs(real), 1)
    int_val = int(int_val)
    int_val = int_val & (conv["int_mask"] >> conv["bin_point"])
    val = int_val
    dec = 0
    dec = dec_val // conv["dec_step"]
    if dec > conv["dec_mask"]:
        dec = conv["dec_mask"]
    dec_val = dec * conv["dec_step"]
    val += dec_val
    if (val - real) > (real - val + conv["dec_step"]):
        dec -= 1
    if sign == 1:
        return conv["sign_mask"] + ((int_val << conv["bin_point"]) &
                conv["int_mask"]) + dec
    else:
        return ((int_val << conv["bin_point"]) & conv["int_mask"]) + dec
