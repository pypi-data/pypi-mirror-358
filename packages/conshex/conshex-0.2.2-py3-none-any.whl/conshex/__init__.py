r"""
ConsHex -- Parsing Made Fun

Homepage:
	https://github.com/construct/construct
    http://construct.readthedocs.org

Hands-on example:
    >>> from conshex import *
    >>> s = Struct(
    ...     "a" / Byte,
    ...     "b" / Short,
    ... )
    >>> print s.parse(b"\x01\x02\x03")
    Container:
        a = 1
        b = 515
    >>> s.build(Container(a=1, b=0x0203))
    b"\x01\x02\x03"
"""

from conshex.core import *
from conshex.debug import *
from conshex.errors import *
from conshex.expr import *
from conshex.helpers import *
from conshex.lazy import *
from conshex.numbers import *
from conshex.string import *
from conshex.version import *
from conshex import lib


#===============================================================================
# metadata
#===============================================================================
__author__ = "Tim Blume <conshex@3nd.io>"
__version__ = version_string

#===============================================================================
# exposed names
#===============================================================================
__all__ = [
    '__author__',
    '__version__',
    'abs_',
    'Adapter',
    'Aligned',
    'AlignedStruct',
    'Array',
    'Area',
    'Bit',
    'BitsInteger',
    'BitsSwapped',
    'BitStruct',
    'BitwisableString',
    'Bitwise',
    'Byte',
    'Bytes',
    'BytesInteger',
    'ByteSwapped',
    'Bytewise',
    'Check',
    'Checksum',
    'Compressed',
    'CompressedLZ4',
    'Computed',
    'Const',
    'Magic',
    'Construct',
    'Container',
    'Debugger',
    'Default',
    'Double',
    'EncryptedSym',
    'EncryptedSymAead',
    'Enum',
    'EnumInteger',
    'EnumIntegerString',
    'Error',
    'ExprAdapter',
    'ExprSymmetricAdapter',
    'ExprValidator',
    'Filter',
    'FixedSized',
    'Flag',
    'FlagsEnum',
    'FocusedSeq',
    'FormatFieldError',
    'FuncPath',
    'globalPrintFalseFlags',
    'globalPrintFullStrings',
    'GreedyBytes',
    'GreedyRange',
    'Half',
    'Hex',
    'HexDump',
    'If',
    'IfThenElse',
    'Index',
    'Indexing',
    'Int',
    'IntegerError',
    'len_',
    'lib',
    'list_',
    'ListContainer',
    'Long',
    'Mapping',
    'max_',
    'min_',
    'NamedTuple',
    'Nibble',
    'NoneOf',
    'NullStripped',
    'NullTerminated',
    'Numpy',
    'obj_',
    'Octet',
    'OffsettedEnd',
    'OneOf',
    'TryParse',
    'Padded',
    'Padding',
    'Pass',
    'Path',
    'Path2',
    'Peek',
    'Pointer',
    'possiblestringencodings',
    'Prefixed',
    'PrefixedArray',
    'Probe',
    'ProcessXor',
    'RawCopy',
    'Rebuffered',
    'RebufferedBytesIO',
    'Rebuild',
    'release_date',
    'Renamed',
    'RepeatUntil',
    'RestreamData',
    'Restreamed',
    'RestreamedBytesIO',
    'Seek',
    'Select',
    'Sequence',
    'setGlobalPrintFalseFlags',
    'setGlobalPrintFullStrings',
    'setGlobalPrintPrivateEntries',
    'Short',
    'Single',
    'Slicing',
    'StopIf',
    'Struct',
    'Subconstruct',
    'sum_',
    'Switch',
    'SymmetricAdapter',
    'Tell',
    'Terminated',
    'this',
    'Transformed',
    'Tunnel',
    'Union',
    'Validator',
    'VarInt',
    'version',
    'version_string',
    'ZigZag',
]
__all__ += ["Int%s%s%s" % (n,us,bln) for n in (8,16,24,32,64) for us in "us" for bln in "bln"]
__all__ += ["Float%s%s" % (n,bln) for n in (16,32,64) for bln in "bln"]
