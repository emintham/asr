[![Build Status](https://travis-ci.org/emintham/asr.svg?branch=master)](https://travis-ci.org/emintham/asr)
[![Code Climate](https://codeclimate.com/github/emintham/asr/badges/gpa.svg)](https://codeclimate.com/github/emintham/asr)

# Collection of Python tools of questionable utility.

This is relatively new code and has not been thoroughly tested. Caveat emptor.

## Modules:

### Debug

`asr.debug.watch` implements a watcher that watches your attribute for changes and reports the sourcefile that changed it, the line at which it was changed, and both new and old values of the attribute. Helpful for debugging-- beats manually adding breakpoints/print statements at all potential mutation sites.


```python
from asr.debug import watch

f = Foo()
f.foo = 1
sentry = watch(f, 'foo') # prints 'Started watching attribute `f.foo`

f.foo = 2   # prints (f.foo): __main__ line 5 => 1 -> 2
f.foo = 3   # prints (f.foo): __main__ line 6 => 2 -> 3

print(sentry.history) # prints (f.foo): line 0 => None -> 1
                      #        (f.foo): __main__ line 5 => 1 -> 2
                      #        (f.foo): __main__ line 6 => 2 -> 3

sentry.close()        # prints 'Stopped watching attribute `f.foo`
```

#### Known Issues
- Does not currently work with descriptors/`@property`.
