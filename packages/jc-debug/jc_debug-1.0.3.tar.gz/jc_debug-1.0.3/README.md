<a id="debug"></a>

# debug

This debug module a class named DebugChannel, instances of which are useful for
adding temporary or conditional debug output to CLI scripts.

The minimal boilerplate is pretty simple:

```python
from debug import DebugChannel

dc=DebugChannel(True)
```

By default, DebugChannels are created disabled (the write no output), so the
`True` above enables `dc` during its instantiation so it needn't be enabled
later.

A more common way of handling this is ...

```python
from argparse import ArgumentParser
from debug import DebugChannel

dc=DebugChannel()

ap=ArgumentParser()
ap.add_argument('--debug',action='store_true',help="Enable debug output.")
opt=ap.parse_args()
dc.enable(opt.debug)

...
```

This enables the `dc` DebugChannel instance only if --debug is given on the
script's command line.

By default, output is sent to stdandard error and formatted as:

    '{label}: [{pid}] {basename}:{line}:{function}: {indent}{message}\n'

There are several variables you can include in DebugChannel's output. See the
DebugChannel docs below for a list.

So, for example, if you want to see how your variables are behaving in a loop,
you might do something like this:

```python
from debug import DebugChannel

dc=DebugChannel(
    True,
    fmt="{label}: {line:3}: {indent}{message}\n"
)

dc("Entering loop ...").indent()
for i in range(5):
    dc(f"{i=}").indent()
    for j in range(3):
        dc(f"{j=}")
    dc.undent()("Done with j loop.")
dc.undent()("Done with i loop.")
```

That gives you this necely indented output. The indent() and undent() methods
are one thing that makes DebugChannels so nice to work with.

    DC:   8: Entering loop ...
    DC:  10:   i=0
    DC:  12:     j=0
    DC:  12:     j=1
    DC:  12:     j=2
    DC:  13:   Done with j loop.
    DC:  10:   i=1
    DC:  12:     j=0
    DC:  12:     j=1
    DC:  12:     j=2
    DC:  13:   Done with j loop.
    DC:  10:   i=2
    DC:  12:     j=0
    DC:  12:     j=1
    DC:  12:     j=2
    DC:  13:   Done with j loop.
    DC:  10:   i=3
    DC:  12:     j=0
    DC:  12:     j=1
    DC:  12:     j=2
    DC:  13:   Done with j loop.
    DC:  10:   i=4
    DC:  12:     j=0
    DC:  12:     j=1
    DC:  12:     j=2
    DC:  13:   Done with j loop.
    DC:  14: Done with i loop.

That's a simple example, but you might be starting to get an idea of how
versatile DebugChannel instances can be.

A DebugChannel can also be used as a function decorator:

```python
import time
from src.debug import DebugChannel

def delay(**kwargs):
    time.sleep(.1)
    return True

dc=DebugChannel(True,callback=delay)
dc.setFormat("{label}: {function}: {indent}{message}\n")

@dc
def example1(msg):
    print(msg)

@dc
def example2(msg,count):
    for i in range(count):
        example1(f"{i+1}: {msg}")

example2("First test",3)
example2("Second test",2)
```

This causes entry into and exit from the decorated function to be recorded in
the given DebugChannel's output. If you put that into a file named foo.py and
then run "python3 -m foo", you'll get this:

```
DC: __main__: example2('First test',3) ...
DC: example2:     example1('1: First test') ...
1: First test
DC: example2:     example1(...) returns None after 45µs.
DC: example2:     example1('2: First test') ...
2: First test
DC: example2:     example1(...) returns None after 29µs.
DC: example2:     example1('3: First test') ...
3: First test
DC: example2:     example1(...) returns None after 26µs.
DC: __main__: example2(...) returns None after 630ms.
DC: __main__: example2('Second test',2) ...
DC: example2:     example1('1: Second test') ...
1: Second test
DC: example2:     example1(...) returns None after 28µs.
DC: example2:     example1('2: Second test') ...
2: Second test
DC: example2:     example1(...) returns None after 23µs.
DC: __main__: example2(...) returns None after 423ms.
```

When outputting a data structure, it's nice to be a little structured about it.
So if you send a list, tuple, dict, or set to a DebugChannel instance as the
whole message, it will be formatted one item at a time in the output.

```python
from debug import DebugChannel

dc=DebugChannel(True,fmt="{label}: {line:3}: {indent}{message}\n")

l="this is a test".split()
s=set(l)
d=dict(zip('abcd',l))

dc("l:")(l)
dc("s:")(s)
dc("d:")(d)
```

Notice the idiom of using dc(...)'s output as the DebugChannel instance itself,
allowing further manipulation in the same "breath." Here's the output:

```python
DC:  12: l:
DC:  12: [
DC:  12:     'this',
DC:  12:     'is',
DC:  12:     'a',
DC:  12:     'test'
DC:  12: ]
DC:  13: s:
DC:  13: {
DC:  13:     'a',
DC:  13:     'is',
DC:  13:     'test',
DC:  13:     'this'
DC:  13: }
DC:  14: d:
DC:  14: {
DC:  14:     'a': 'this',
DC:  14:     'b': 'is',
DC:  14:     'c': 'a',
DC:  14:     'd': 'test'
DC:  14: }
```

Notice sets are output in alphabetical order (according to their repr()
values). Since sets are unordered by nature, this makes them easier to inspect
visually without misrepresenting their contents.

That's a very general start. See DebugChannel's class docs for more.

<a id="debug.DebugChannel"></a>

## DebugChannel Objects

```python
class DebugChannel()
```

Objects of this class are useful for debugging, and this is even
more powerful when combined with loggy.LogStream to write all debug
output to some appropriate syslog facility. Here's an example, put
into an executable script called dc-log-test:

```python
#!/usr/bin/env python

from debug import DebugChannel
from loggy import LogStream

dc=DebugChannel(
    True,
    stream=LogStream(facility='user'),
    fmt='{label}: {basename}({line}): {indent}{message}\n'
)
dc('Testing')
```

The output in /var/log/user.log (which might be a different path on
your system) might look like this:

    Aug 16 22:58:16 pi4 x[18478] DC: dc-log-test(11): Testing

What I really like about this is that the source filename and line
number are included in the log output. The "dc('Testing')" call is on
line 11 of dc-log-test.

Run this module directly with

    python3 -m debug

to see a demonstration of indenture. The example code for that demo
is at the bottom of the debug.py source file.

IGNORING MODULES:
DebugChannel.write() goes to some length to ensure the filename and
line number reported in its output are something helpful to the
caller. For instance, the source line shouldn't be anything in this
DebugChannel class.

Use the ignoreModule() method to tell the DebugChannel object ignore
other modules, and optionally, specific functions within that
module.

<a id="debug.DebugChannel.__init__"></a>

#### \_\_init\_\_

```python
def __init__(enabled=False,
             stream=sys.stderr,
             label="DC",
             indent_with="    ",
             fmt="{label}: {basename}:{line}:{function}: {indent}{message}\n",
             date_fmt="%Y-%m-%d",
             time_fmt="%H:%M:%S",
             time_tupler=localtime,
             callback=None)
```

Initialize this new DebugChannel instance.

**Arguments**:


  * enabled: True if this DebugChannel object is allowed to
  output messages. False if it should be quiet.
  * stream: The stream (or stream-like object) to write
  messages to.
  * label: A string indicated what we're doing.
  * indent_with: Indenting uses this string value.
  * fmt: Format of debug output. See setFormat().
  * date_fmt: strftime() uses this string to format dates.
  * time_fmt: strftime() uses this string to format times.
  * time_tupler: This is either time.localtime or time.gmtime and
  defaults to localtime.
  * callback: A function accepting keyword arguments and returning
  True if the current message is to be output. The keyword
  arguments are all the local variables of DebugChannel.write().
  Of particular interest might be "stack" and all the variables
  available for formatting (label, basename, pid, function, line,
  indent, and message).

<a id="debug.DebugChannel.__bool__"></a>

#### \_\_bool\_\_

```python
def __bool__()
```

Return the Enabled state of this DebugChannel object. It is
somtimes necessary to logically test whether our code is in
debug mode at runtime, and this method makes that very simple.

```python
d=DebugChannel(opt.debug)
.
.
.
if d:
    d("Getting diagnostics ...")
    diagnostics=get_some_computationally_expensive_data()
    d(diagnostics)
```

<a id="debug.DebugChannel.enable"></a>

#### enable

```python
def enable(state=True)
```

Allow this DebugChannel object to write messages if state is
True. Return the previous state as a boolean.

<a id="debug.DebugChannel.disable"></a>

#### disable

```python
def disable()
```

Inhibit output from this DebugChannel object, and return its
previous "enabled" state.

<a id="debug.DebugChannel.ignoreModule"></a>

#### ignoreModule

```python
def ignoreModule(name, *args)
```

Given the name of a module, e.g. "debug"), ignore any entries
in our call stack from that module. Any subsequent arguments
must be the names of functions to be ignored within that module.
If no such functions are named, all calls from that module will
be ignored.

<a id="debug.DebugChannel.setDateFormat"></a>

#### setDateFormat

```python
def setDateFormat(fmt)
```

Use the formatting rules of strftime() to format the "date"
value to be output in debug messages. Return the previous date
format string.

<a id="debug.DebugChannel.setTimeFormat"></a>

#### setTimeFormat

```python
def setTimeFormat(fmt)
```

Use the formatting rules of strftime() to format the "time"
value to be output in debug messages. Return the previous time
format string.

<a id="debug.DebugChannel.setIndentString"></a>

#### setIndentString

```python
def setIndentString(s)
```

Set the string to indent string. Return this DebugChannel
object. E.g. at indent level 3, the "{indent}" portion of the
formatted debug will contain 3 copies of the string you set with
this function. So '  ' will indent two spaces per indention
level. Another popular choice is '| ' to make longer indention
runs easier to follow in the debug output.

<a id="debug.DebugChannel.setFormat"></a>

#### setFormat

```python
def setFormat(fmt)
```

Set the format of our debug statements. The format defaults
to:

  '{label}: {basename}:{line}:{function}: {indent}{message}\n'

Fields:
* {date}: current date (see setDateFormat())
* {time}: current time (see setTimeFormat())
* {pid}: numeric ID of the current process
* {label}: what type of thing is getting logged (default: 'DC')
* {pathname}: full path of the calling source file
* {basename}: base name of the calling source file
* {function}: name of function debug.write() was called from
* {line}: number of the calling line of code in its source file
* {code}: the Python code at the given line of the given file
* {indent}: indent string multiplied by the indention level
* {message}: the message to be written

All non-field text is literal text. The '\n' at the end is
required if you want a line ending at the end of each message.
If your DebugChannel object is configured to write to a
LogStream object that writes to syslog or something similar, you
might want to remove the {date} and {time} (and maybe {label})
fields from the default format string to avoid logging these
values redundantly.

<a id="debug.DebugChannel.indent"></a>

#### indent

```python
def indent(indent=1)
```

Increase this object's current indenture by this value (which
might be negative. Return this DebugChannel opject with the
adjusted indenture. See write() for how this might be used.

<a id="debug.DebugChannel.undent"></a>

#### undent

```python
def undent(indent=1)
```

Decrease this object's current indenture by this value (which
might be negative. Return this DebugChannel object with the
adjusted indenture. See write() for how this might be used.

<a id="debug.DebugChannel.writelines"></a>

#### writelines

```python
def writelines(seq)
```

Just a wrapper around write(), since that method handles
sequences (and other things) just fine. writelines() is only
provided for compatibility with code that expects it to be
supported.

<a id="debug.DebugChannel.__call__"></a>

#### \_\_call\_\_

```python
def __call__(arg, *args, **kwargs)
```

If this DebugChannel instance is simply being called, this
method is a very simple wrapper around the write(...) emthod. If
it is being used as a function decorator, that function entry
and exit are recorded to the DebugChannel, and this becomes a
more featuresome wrapper around the write(...) method.

<a id="debug.DebugChannel.writeTraceback"></a>

#### writeTraceback

```python
def writeTraceback(exc)
```

Write the given exception with traceback information to our
output stream.

<a id="debug.DebugChannel.write"></a>

#### write

```python
def write(message)
```

If this debug instance is enabled, write the given message
using the our current format. In any case, return this
DebugChannel instance so further operations can be performed on
it. E.g.:

```python
debug=DebugChannel(opt.debug)
debug('Testing')

def func(arg):
    debug.write("Entering func(arg=%r)"%(arg,)).indent(1)
    for i in range(3):
        debug(f"{i=}")
    debug.indent(-1).write("Leaving func(...) normally")
```

This lets the caller decide whether to change indenture among
other things before or after the message is written.

If message is a single string containing no line endings, that
single value will be outout. if message contains at least one
newline (the value of os.linesep), each line is output on a
debug line of its own.

If message is a list or tuple, each item in that sequence will
be output on its own line.

If message is a dictionary, each key/value pair is written out
as "key: value" to its own log line.

<a id="debug.line_iter"></a>

#### line\_iter

```python
def line_iter(s)
```

This iterator facilitates stepping through each line of a multi-
line string in place, without having to create a list containing
those lines. This is similar to `str.splitlines()`, but it yields
slices of the original string rather than returning a list of copies
of segments of the original.
