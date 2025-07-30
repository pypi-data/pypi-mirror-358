import pytest,re,sys,time
from io import StringIO
from src.debug import DebugChannel
from pprint import pprint

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# We'll be sending debug output to this stream so we can write tests
# against its content.

out=StringIO()

def clear_output(output_stream=out):
    "Remove any data written to this output stream."

    output_stream.seek(0)
    output_stream.truncate(0)

def outstr(output_stream=out):
    """Return the content of the given output_stream and leave that
    stream in an empty state."""

    s=output_stream.getvalue()
    output_stream.seek(0)
    output_stream.truncate(0)
    return s

def outstr_lines(output_stream=out):
    "Same as outstr(), but returns a sequence of lines."

    return tuple(outstr().split('\n'))


dc=DebugChannel(True,stream=out)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Test code begins here.

@dc
def exception_test():
    x=1/0

@dc
def subtest():
    dc('MULTILINE OUTPUT ...\n').indent()
    dc('MULTILINE\nOUTPUT\n...\n')
    dc.undent()('LIST OUTPUT ...')
    dc('LIST OUTPUT ...'.split())
    dc('TUPLE OUTPUT ...')
    dc(tuple('TUPLE OUTPUT'.split()))
    dc('DICTIONARY OUTPUT ...')
    dc(dict(a='dictionary',c='output',b='blah'))
    dc('DONE!')

class Tests:
    def test_basics(self):
        dc.setFormat("{label}: {function}: {indent}{message}\n")

        assert dc.enabled is True
        assert bool(dc) is True
        dc('DISABLING OUTPUT ...').indent()
        prev=dc.enable(False)
        assert prev is True
        assert dc.enabled is False
        dc("Disabled debug output (so you shouldn't see this).")
        prev=dc.enable(prev)
        assert prev is False
        assert dc.enabled is True
        dc.undent()('RE-ENABLED OUTPUT ...')
        assert outstr()=="""\
DC: test_basics: DISABLING OUTPUT ...
DC: test_basics: RE-ENABLED OUTPUT ...
"""

        assert dc.indlev==0
        dc('BASIC OUTPUT ...').indent()
        assert dc.indlev==1
        dc('Message 1')
        assert dc.indlev==1
        dc('Message 2')
        dc.undent()
        assert outstr()=="""\
DC: test_basics: BASIC OUTPUT ...
DC: test_basics:     Message 1
DC: test_basics:     Message 2
"""
        assert dc.indlev==0

        # Test tuple output.
        dc(('a',2,True))
        assert outstr()=="""\
DC: test_basics: (
DC: test_basics:     'a',
DC: test_basics:     2,
DC: test_basics:     True
DC: test_basics: )
"""

        # Test list output.
        dc(['a',2,True])
        assert outstr()=="""\
DC: test_basics: [
DC: test_basics:     'a',
DC: test_basics:     2,
DC: test_basics:     True
DC: test_basics: ]
"""

        # Test set output.
        dc(set(['a',2,True]))
        assert outstr()=="""\
DC: test_basics: {
DC: test_basics:     'a',
DC: test_basics:     2,
DC: test_basics:     True
DC: test_basics: }
"""

        # Test dictionary output.
        dc({'a':1,2:'b','c':True})
        assert outstr()=="""\
DC: test_basics: {
DC: test_basics:     'a': 1,
DC: test_basics:     2: 'b',
DC: test_basics:     'c': True
DC: test_basics: }
"""

        @dc
        def example1(msg):
            print(msg)

        @dc
        def example2(msg,count):
            for i in range(count):
                example1(f"{i+1}: {msg}")

        example2("First test",3)
        expected=(
            re.escape("DC: test_basics: example2('First test',3) ..."),
            re.escape("DC: example2:     example1('1: First test') ..."),
            re.escape("DC: example2:     example1(...) returns None after ")+".*$",
            re.escape("DC: example2:     example1('2: First test') ..."),
            re.escape("DC: example2:     example1(...) returns None after ")+".*$",
            re.escape("DC: example2:     example1('3: First test') ..."),
            re.escape("DC: example2:     example1(...) returns None after ")+".*$",
            re.escape("DC: test_basics: example2(...) returns None after ")+".*$",
            re.escape(""),
        )
        for line,regexp in zip(outstr_lines(),expected):
            assert re.match(regexp,line)

        example2("Second test",2)
        expected=(
            re.escape("DC: test_basics: example2('Second test',2) ..."),
            re.escape("DC: example2:     example1('1: Second test') ..."),
            re.escape("DC: example2:     example1(...) returns None after ")+".*$",
            re.escape("DC: example2:     example1('2: Second test') ..."),
            re.escape("DC: example2:     example1(...) returns None after ")+".*$",
            re.escape("DC: test_basics: example2(...) returns None after ")+".*$",
            re.escape(""),
        )
        for line,regexp in zip(outstr_lines(),expected):
            assert re.match(regexp,line)

    def test_exception_output(self):
        """Make lots of calls to our DebugChannel object to put it
        through its paces."""

        try:
            exception_test()
        except Exception as e:
            dc.writeTraceback(e)

        expected=(
            r'DC: test_exception_output: exception_test\(\) \.\.\.',
            r'DC: test_exception_output:     Traceback \(most recent call last\):',
            r'DC: test_exception_output:       File ".*?/src/debug/tests/test_operations.py", line \d+, in test_exception_output',
            r'DC: test_exception_output:         exception_test\(\)',
            r'DC: test_exception_output:         ~~~~~~~~~~~~~~\^\^',
            r'DC: test_exception_output:       File ".*?/src/debug/src/debug/__init__.py", line \d+, in f',
            r'DC: test_exception_output:         ret = arg\(\*args, \*\*kwargs\)',
           r'DC: test_exception_output:       File ".*?/src/debug/tests/test_operations.py", line \d+, in exception_test',
            r'DC: test_exception_output:         x=1/0',
            r'DC: test_exception_output:           ~\^~',
            r'DC: test_exception_output:     ZeroDivisionError: division by zero',
            r'',
        )
        for line,regexp in zip(outstr_lines(),expected):
            assert re.match(regexp,line), f"{regexp} doesn't match {line}"
