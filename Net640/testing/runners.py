from django.test.runner import DiscoverRunner
from django.test import TransactionTestCase, TestCase
from unittest.suite import TestSuite


class TransactionTestRunner(DiscoverRunner):
    """
    to run tests with this runner execute following command
    python manage.py test --testrunner "Net640.testing.runners.TransactionTestRunner"
    """

    def build_suite(self, *args, **kwargs):
        suite = super().build_suite(*args, **kwargs)
        tests = [t for t in suite._tests if self.is_transactiontest(t)]
        return TestSuite(tests=tests)

    def is_transactiontest(self, test):
        return hasattr(test, "TRANSACTION_TEST_CASE")


class UnitTestRunner(DiscoverRunner):
    """
    to run tests with this runner execute following command
    python manage.py test --testrunner "Net640.testing.runners.UnitTestRunner"
    """

    def build_suite(self, *args, **kwargs):
        suite = super().build_suite(*args, **kwargs)
        tests = [t for t in suite._tests if self.is_unittest(t)]
        return TestSuite(tests=tests)

    def is_unittest(self, test):
        return not hasattr(test, "TRANSACTION_TEST_CASE")
