###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
from __future__ import absolute_import
from __future__ import print_function

__docformat__ = "reStructuredText"

import doctest
import unittest

import m01.fake
import m01.fake.testing
import m01.stub.testing


def test_suite():
    return unittest.TestSuite((
        # fake mongo
        doctest.DocFileSuite('fake.txt',
            setUp=m01.fake.testing.setUpFakeMongo,
            tearDown=m01.fake.testing.setUpFakeMongo,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            checker=m01.fake.reNormalizer
            ),
        # stub mongod
        doctest.DocFileSuite('README.txt',
            setUp=m01.stub.testing.setUpStubMongo,
            tearDown=m01.stub.testing.tearDownStubMongo,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            checker=m01.fake.reNormalizer
            ),
        # run twice for test teardown
        doctest.DocFileSuite('second.txt',
            setUp=m01.stub.testing.setUpStubMongo,
            tearDown=m01.stub.testing.tearDownStubMongo,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            checker=m01.fake.reNormalizer),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
