"""
Pure-Python implementation of a Python 3-like bytes object for Python 2.

Why do this? Without it, the Python 2 bytes object is a very, very
different beast to the Python 3 bytes object. Running the
test_bytes_from_py33.py script from the Python 3.3 test suite using
Python 2 with its default str-aliased bytes object (after the appropriate
import fixes, and using the backported test.support module) yields this:
    ------------------------------------------------------------------
    Ran 203 tests in 0.214s
    
    FAILED (failures=31, errors=55, skipped=1)
    ------------------------------------------------------------------
when running

    $ python -m future.tests.test_bytes_from_py33

"""

from collections import Iterable

from future.utils import PY3
from future.builtins.backports import no, issubset


_builtin_bytes = bytes


class newbytes(_builtin_bytes):
    """
    A backport of the Python 3 bytes object to Py2
    """
    def __new__(cls, *args, **kwargs):
        """
        From the Py3 bytes docstring:

        bytes(iterable_of_ints) -> bytes
        bytes(string, encoding[, errors]) -> bytes
        bytes(bytes_or_buffer) -> immutable copy of bytes_or_buffer
        bytes(int) -> bytes object of size given by the parameter initialized with null bytes
        bytes() -> empty bytes object
        
        Construct an immutable array of bytes from:
          - an iterable yielding integers in range(256)
          - a text string encoded using the specified encoding
          - any object implementing the buffer API.
          - an integer
        """
        
        if len(args) == 0:
            return super(newbytes, cls).__new__(cls)
        elif isinstance(args[0], newbytes):
            return args[0]
        elif isinstance(args[0], _builtin_bytes):
            value = args[0]
        elif isinstance(args[0], unicode):
            if 'encoding' not in kwargs:
                raise TypeError('unicode string argument without an encoding')
            value = args[0].encode(**kwargs)
        elif isinstance(args[0], Iterable):
            if len(args[0]) == 0:
                # What is this?
                raise ValueError('unknown argument type')
            elif len(args[0]) > 0 and isinstance(args[0][0], int):
                # It's a list of integers
                value = b''.join([chr(x) for x in args[0]])
            else:
                raise ValueError('item cannot be interpreted as an integer')
        elif isinstance(args[0], int):
            if args[0] < 0:
                raise ValueError('negative count')
            value = b'\x00' * args[0]
        else:
            value = args[0]
        return super(newbytes, cls).__new__(cls, value)
        
    def __repr__(self):
        return 'b' + super(newbytes, self).__repr__()

    def __str__(self):
        return 'b' + "'{}'".format(super(newbytes, self).__str__())

    def __getitem__(self, y):
        value = super(newbytes, self).__getitem__(y)
        if isinstance(y, int):
            return ord(value)
        else:
            return newbytes(value)

    def __contains__(self, key):
        if isinstance(key, int):
            newbyteskey = newbytes([key])
        elif isinstance(key, newbytes):
            newbyteskey = key
        else:
            newbyteskey = newbytes(key)
        return issubset(list(newbyteskey), list(self))
    
    @no(unicode)
    def __add__(self, other):
        return newbytes(super(newbytes, self).__add__(other))

    @no(unicode)
    def __radd__(self, left):
        return newbytes(left) + self
            
    def join(self, iterable_of_bytes):
        errmsg = 'sequence item {}: expected bytes, found unicode string'
        for i, item in enumerate(iterable_of_bytes):
            if isinstance(item, unicode):
                raise TypeError(errmsg.format(i))
        return newbytes(super(newbytes, self).join(iterable_of_bytes))

    @classmethod
    def fromhex(cls, string):
        # Only on Py2:
        return cls(string.replace(' ', '').decode('hex'))

    @no(unicode)
    def find(self, sub, *args):
        return newbytes(super(newbytes, self).find(sub, *args))

    @no(unicode)
    def rfind(self, sub, *args):
        return newbytes(super(newbytes, self).rfind(sub, *args))

    @no(unicode, (1, 2))
    def replace(self, old, new, *args):
        return newbytes(super(newbytes, self).replace(old, new, *args))

    def encode(self, *args):
        raise AttributeError("encode method has been disabled in newbytes")

    def decode(self, encoding='utf-8', errors='strict'):
        """
        Returns a newstr (i.e. unicode subclass)

        Decode B using the codec registered for encoding. Default encoding
        is 'utf-8'. errors may be given to set a different error
        handling scheme.  Default is 'strict' meaning that encoding errors raise
        a UnicodeDecodeError.  Other possible values are 'ignore' and 'replace'
        as well as any other name registered with codecs.register_error that is
        able to handle UnicodeDecodeErrors.
        """
        from future.builtins.backports.newstr import newstr
        return newstr(super(newbytes, self).decode(encoding, errors))
        
    @no(unicode)
    def startswith(self, prefix, *args):
        return super(newbytes, self).startswith(prefix, *args)

    @no(unicode)
    def endswith(self, prefix, *args):
        return super(newbytes, self).endswith(prefix, *args)

    @no(unicode)
    def split(self, sep=None, maxsplit=-1):
        # Py2 str.split() takes maxsplit as an optional parameter, not as a
        # keyword argument as in Python 3 bytes.
        parts = super(newbytes, self).split(sep, maxsplit)
        return [newbytes(part) for part in parts]

    @no(unicode)
    def rsplit(self, sep=None, maxsplit=-1):
        # Py2 str.rsplit() takes maxsplit as an optional parameter, not as a
        # keyword argument as in Python 3 bytes.
        parts = super(newbytes, self).rsplit(sep, maxsplit)
        return [newbytes(part) for part in parts]

    @no(unicode)
    def partition(self, sep):
        parts = super(newbytes, self).partition(sep)
        return tuple(newbytes(part) for part in parts)

    @no(unicode)
    def rpartition(self, sep):
        parts = super(newbytes, self).rpartition(sep)
        return tuple(newbytes(part) for part in parts)

    @no(unicode)
    def index(self, sub, *args):
        '''
        Returns index of sub in bytes.
        Raises ValueError if byte is not in bytes and TypeError if can't
        be converted bytes or its length is not 1.
        '''
        if isinstance(sub, int):
            if len(args) == 0:
                start, end = 0, len(self)
            elif len(args) == 1:
                start = args[0]
            elif len(args) == 2:
                start, end = args
            else:
                raise TypeError('takes at most 3 arguments')
            return list(self)[start:end].index(sub)
        if not isinstance(sub, bytes):
            try:
                sub = self.__class__(sub)
            except (TypeError, ValueError):
                raise TypeError("can't convert sub to bytes")
        try:
            return super(newbytes, self).index(sub, *args)
        except ValueError:
            raise ValueError('substring not found')

    def __eq__(self, other):
        if isinstance(other, _builtin_bytes):
            return super(newbytes, self).__eq__(other)
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, _builtin_bytes):
            return super(newbytes, self).__ne__(other)
        else:
            return True


__all__ = ['newbytes']