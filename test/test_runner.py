import sys
import unittest

import os
from xmlrunner import XMLTestRunner

from mycroft.configuration import ConfigurationManager

__author__ = 'seanfitz'

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = os.path.dirname(os.path.dirname(__file__))

loader = unittest.TestLoader()
fail_on_error = "--fail-on-error" in sys.argv
ConfigurationManager.load_local([os.path.join(TEST_DIR, 'mycroft.ini')])
tests = loader.discover(TEST_DIR, pattern="*_test*.py")
runner = XMLTestRunner(output="./build/report/tests")
result = runner.run(tests)
if fail_on_error and len(result.failures + result.errors) > 0:
    sys.exit(1)
