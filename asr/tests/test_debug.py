from unittest import TestCase

from asr.debug import watch


class Foo(object):
    foo = 1
    bar = 1


class WatchTests(TestCase):
    """
    Tests for watch class.
    """

    @classmethod
    def setUpClass(cls):
        cls.old_getattribute = Foo.__getattribute__
        cls.old_setattr = Foo.__setattr__

    def setUp(self):
        # assert class is unpatched after each test case
        self.assertIs(Foo.__getattribute__, self.__class__.old_getattribute)
        self.assertIs(Foo.__setattr__, self.__class__.old_setattr)
        self.sentry = None

    def tearDown(self):
        if self.sentry:
            self.sentry.close()

    def test_changes_are_recorded(self):
        f = Foo()

        self.sentry = watch(f, 'foo', verbose=False)
        self.assertEqual(self.sentry.value, 1)

        f.foo = 2
        self.assertEqual(self.sentry.value, 2)

        # line_num of change, old value, new value
        expected = [(0, None, 1),
                    (37, 1, 2)]
        self.assertEqual([(lineno, old, new)
                          for _, lineno, old, new in self.sentry.values],
                         expected)

    def test_other_attrs_are_unaffected(self):
        f = Foo()
        self.sentry = watch(f, 'foo', verbose=False)
        self.assertEqual(f.bar, 1)

        f.foo = 2
        self.assertEqual(f.foo, 2)
        self.assertEqual(f.bar, 1)

    def test_label_inferred_if_present(self):
        f = Foo()

        self.sentry = watch(f, 'foo', verbose=False)
        self.assertEqual(self.sentry.label, 'f.foo')

    def test_patch_and_unpatch(self):
        f = Foo()

        self.sentry = watch(f, 'foo', verbose=False)

        self.assertFalse(Foo.__getattribute__ is self.__class__.old_getattribute)
        self.assertFalse(Foo.__setattr__ is self.__class__.old_setattr)
        self.assertFalse(self.__class__.old_getattribute(f, 'foo') is f.foo)
        self.assertEqual(f.foo, 1)

        self.sentry.close()

        self.assertIs(Foo.__getattribute__, self.__class__.old_getattribute)
        self.assertIs(Foo.__setattr__, self.__class__.old_setattr)
        self.assertIs(self.__class__.old_getattribute(f, 'foo'), f.foo)
        self.assertEqual(f.foo, 1)
