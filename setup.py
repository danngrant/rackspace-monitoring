# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
import doctest

from distutils.core import setup
from distutils.core import Command
from unittest import TextTestRunner, TestLoader
from glob import glob
from subprocess import call
from os.path import splitext, basename, join as pjoin


HTML_VIEWSOURCE_BASE = 'https://github.com/racker/libcloud-monitoring'
PROJECT_BASE_DIR = ''
TEST_PATHS = ['test']

def read_version_string():
    version = None
    sys.path.insert(0, pjoin(os.getcwd()))
    from libcloud_monitoring import __version__
    version = __version__
    sys.path.pop(0)
    return version

class TestCommand(Command):
    description = "run test suite"
    user_options = []

    def initialize_options(self):
        THIS_DIR = os.path.abspath(os.path.split(__file__)[0])
        sys.path.insert(0, THIS_DIR)
        for test_path in TEST_PATHS:
            sys.path.insert(0, pjoin(THIS_DIR, test_path))
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        try:
            import mock
            mock
        except ImportError:
            print 'Missing "mock" library. mock is library is needed ' + \
                  'to run the tests. You can install it using pip: ' + \
                  'pip install mock'
            sys.exit(1)

        status = self._run_tests()
        sys.exit(status)

    def _run_tests(self):
        secrets = pjoin(self._dir, 'test', 'secrets.py')
        if not os.path.isfile(secrets):
            print "Missing %s" % (secrets)
            print "Maybe you forgot to copy it from -dist:"
            print "  cp test/secrets.py-dist test/secrets.py"
            sys.exit(1)

        pre_python26 = (sys.version_info[0] == 2
                        and sys.version_info[1] < 6)
        if pre_python26:
            missing = []
            # test for dependencies
            try:
                import simplejson
                simplejson              # silence pyflakes
            except ImportError:
                missing.append("simplejson")

            try:
                import ssl
                ssl                     # silence pyflakes
            except ImportError:
                missing.append("ssl")

            if missing:
                print "Missing dependencies: %s" % ", ".join(missing)
                sys.exit(1)

        testfiles = []
        for test_path in TEST_PATHS:
            for t in glob(pjoin(self._dir, test_path, 'test_*.py')):
                testfiles.append('.'.join(
                    [test_path.replace('/', '.'), splitext(basename(t))[0]]))

        tests = TestLoader().loadTestsFromNames(testfiles)

        t = TextTestRunner(verbosity = 2)
        res = t.run(tests)
        return not res.wasSuccessful()


class Pep8Command(Command):
    description = "run pep8 script"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import pep8
            pep8
        except ImportError:
            print 'Missing "pep8" library. You can install it using pip: ' + \
                  'pip install pep8'
            sys.exit(1)

        cwd = os.getcwd()
        retcode = call(('pep8 %s/libcloud_monitoring/ %s/test/' %
                (cwd, cwd)).split(' '))
        sys.exit(retcode)


class ApiDocsCommand(Command):
    description = "generate API documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system(
            'pydoctor'
            ' --add-package=libcloud_monitoring'
            ' --project-name="Libcloud Monitoring"'
            ' --make-html'
            ' --html-viewsource-base="%s"'
            ' --project-base-dir=`pwd`'
            ' --project-url="%s"'
            % (HTML_VIEWSOURCE_BASE, PROJECT_BASE_DIR)
        )

class CoverageCommand(Command):
    description = "run test suite and generate coverage report"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import coverage
        cov = coverage.coverage(config_file='.coveragerc')
        cov.start()

        tc = TestCommand(self.distribution)
        tc._run_tests()

        cov.stop()
        cov.save()
        cov.html_report()

setup(
    name='libcloud-monitoring',
    version=read_version_string(),
    description='Client library for Rackspace Monitoring',
    author='Rackspace',
    author_email='',
    requires=(['apache_libcloud(>=0.7.1)']),
    packages=[
        'libcloud_monitoring',
        'libcloud_monitoring.drivers',
    ],
    package_dir={
        'libcloud_monitoring': 'libcloud_monitoring',
    },
    license='Apache License (2.0)',
    url='http://libcloud.apache.org/',
    cmdclass={
        'test': TestCommand,
        'pep8': Pep8Command,
        'apidocs': ApiDocsCommand,
        'coverage': CoverageCommand
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
