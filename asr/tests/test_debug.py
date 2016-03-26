from unittest import TestCase

from asr.debug import watch


class Foo(object):
    pass


class WatchTests(TestCase):
    """
    Tests for watch class.
    """

    def test_changes_are_recorded(self):
        f = Foo()
        f.foo = 1

        sentry = watch(f, 'foo', verbose=False)
        self.assertEqual(sentry.value, 1)

        f.foo = 2
        sentry.close()

        self.assertEqual(sentry.value, 2)

        # line_num of change, old value, new value
        expected = [(0, None, 1),
                    (22, 1, 2)]
        self.assertEqual([(lineno, old, new)
                          for _, lineno, old, new in sentry.values],
                         expected)

    def test_label(self):
        f = Foo()
        f.foo = 1

        sentry = watch(f, 'foo', verbose=False)
        sentry.close()

        self.assertEqual(sentry.label, 'f.foo')

    def test_patch_and_unpatch(self):
        f = Foo()
        f.foo = 1

        old_getattribute = Foo.__getattribute__
        old_setattr = Foo.__setattr__

        sentry = watch(f, 'foo', verbose=False)

        self.assertFalse(Foo.__getattribute__ is old_getattribute)
        self.assertFalse(Foo.__setattr__ is old_setattr)
        self.assertFalse(old_getattribute(f, 'foo') is f.foo)
        self.assertEqual(f.foo, 1)

        sentry.close()

        self.assertIs(Foo.__getattribute__, old_getattribute)
        self.assertIs(Foo.__setattr__, old_setattr)
        self.assertIs(old_getattribute(f, 'foo'), f.foo)
        self.assertEqual(f.foo, 1)
