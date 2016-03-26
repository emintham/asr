from six import iteritems


__all__ = ('watch', )


def get_nth_frame(level=0):
    """
    Get the frame of the n-th caller. Returns the bottom-most frame
    if n > stack size - 1.  0 is the current frame.
    """
    import inspect
    curr_frame = inspect.currentframe()

    try:
        for _ in range(level):
            curr_frame = curr_frame.f_back
    except AttributeError:
        pass

    return curr_frame


class VarNotFound(Exception):
    """Raised when an object is not found in a caller's local scope."""
    pass


class watch(object):
    """
    Watches an attribute for changes in value.

    Args:
        obj: the object the attribute is attached to
        attr: the attribute being watched
        name: name of variable within the local scope. Useful when the
              variable is not directly referenced locally.
              e.g. `self.foo.bar`. Optional.
        max_display_len: maximum length to display each value. Optional.
                         Default is 100.
        verbose: verbose output-- prints changes as it is observed. Optional.
                 Default is True.

    Usage:
        x = Foo()
        x.foo = 500
        sentry = watch(x, 'foo')
        x.foo = 600 # => prints `(x.foo): __main__ line 4 => 500 -> 600`
        sentry.close()
    """

    def __init__(self, obj, attr, name='', max_display_len=100, verbose=True):
        if not hasattr(obj, attr):
            raise AttributeError('`{}` not found on {}!'.format(attr, obj))

        value = getattr(obj, attr)
        klass = obj.__class__
        self.obj = obj
        # filename, line number, old value, new value
        self.values = [('', 0, None, value)]
        self.varname = name or self.get_varname_in_caller_locals(obj)
        self.attr = attr
        self.verbose = verbose
        self.max_display_len = max_display_len
        setattr(self.obj, self.attr, self)

        self.old_getattribute = klass.__getattribute__

        def get_attribute(instance, attribute):
            if attribute != attr or instance is not obj:
                return self.old_getattribute(instance, attribute)

            return self.value

        klass.__getattribute__ = get_attribute

        self.old_setattr = klass.__setattr__

        def set_attribute(instance, attribute, new_val):
            if attribute != attr or instance is not obj:
                self.old_setattr(instance, attribute, new_val)

            frame = get_nth_frame(2)
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno

            if self.verbose:
                print(self.change_as_str(
                    filename, lineno, self.value, new_val))

            self.values.append((filename, lineno, self.value, new_val))

        klass.__setattr__ = set_attribute

        if self.verbose:
            print('Started watching attribute `{}`'.format(self.label))

    def __unicode__(self):
        return u'{} being watched'.format(self.label)

    @property
    def label(self):
        return self.varname + '.' + self.attr

    @property
    def value(self):
        return self.values[-1][-1]

    @property
    def history(self):
        return [self.change_as_str(*entry) for entry in self.values]

    def get_varname_in_caller_locals(self, obj, level=3):
        """
        Returns the variable name of an object within the local scope of the
        n-th level caller.
        """
        frame_locals = get_nth_frame(level).f_locals

        for k, v in iteritems(frame_locals):
            if v is obj:
                return k
        else:
            error_message = ('{} was not found in the {}-th level caller\'s '
                             'local scope! Provide a `name` argument instead.'
                             ).format(obj, level)
            raise VarNotFound(error_message)

    def change_as_str(self, filename, line_num, old_value, new_value):
        old_value = str(old_value)
        if len(old_value) > self.max_display_len:
            old_value = old_value[:self.max_display_len-3] + '...'

        new_value = str(new_value)
        if len(new_value) > self.max_display_len:
            new_value = new_value[:self.max_display_len-3] + '...'

        return '({}): {} line {} => {} -> {}'.format(
            self.label, filename, line_num, old_value, new_value)

    def close(self):
        """Unpatches the object and its class"""
        klass = self.obj.__class__
        klass.__getattribute__ = self.old_getattribute
        klass.__setattr__ = self.old_setattr
        setattr(self.obj, self.attr, self.value)

        if self.verbose:
            print('Stopped watching attribute `{}`'.format(self.label))
