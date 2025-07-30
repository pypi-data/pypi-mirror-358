##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import doctest
import re
import unittest

import zope.traversing.testing
from z3c.batching.batch import Batch
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest
from zope.site.testing import siteSetUp
from zope.site.testing import siteTearDown
from zope.testing.renormalizing import RENormalizing

from z3c.table import batch
from z3c.table import column
from z3c.table import interfaces
from z3c.table import table
from z3c.table import testing


class FakeContainer:
    def values(self):
        pass


marker_pos = object()
marker_kws = object()


class InterfaceBaseTest:
    """Base test for IContainer including interface test."""

    iface = None
    klass = None
    pos = marker_pos
    kws = marker_kws

    def getTestPos(self):
        return self.pos

    def getTestKws(self):
        return self.kws

    def makeTestObject(self, object=None, *pos, **kws):
        # provide default positional or keyword arguments
        ourpos = self.getTestPos()
        if ourpos is not marker_pos and not pos:
            pos = ourpos

        ourkws = self.getTestKws()
        if ourkws is not marker_kws and not kws:
            kws = ourkws

        testclass = self.getTestClass()

        if object is None:
            # a class instance itself is the object to be tested.
            return testclass(*pos, **kws)
        else:
            # an adapted instance is the object to be tested.
            return testclass(object, *pos, **kws)

    def test_verifyObject(self):
        # object test
        self.assertTrue(
            verifyObject(self.getTestInterface(), self.makeTestObject())
        )


# table
class TestTable(InterfaceBaseTest, unittest.TestCase):
    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.ITable

    def getTestClass(self):
        return table.Table

    def getTestPos(self):
        return (FakeContainer(), TestRequest())


class TestSequenceTable(InterfaceBaseTest, unittest.TestCase):
    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.ITable

    def getTestClass(self):
        return table.SequenceTable

    def getTestPos(self):
        return (None, TestRequest())


# column
class TestColumn(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.Column

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)

    def test_renderHeadCell(self):
        context = Mock()
        tbl = Mock()
        col = column.Column(context, TestRequest(), tbl)
        col.header = "FooBar"
        self.assertEqual(col.renderHeadCell(), "FooBar")

        col.header = '14" <monitor>'
        self.assertEqual(col.renderHeadCell(), "14&quot; &lt;monitor&gt;")


class TestNoneCell(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.INoneCell

    def getTestClass(self):
        return column.NoneCell

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestNameColumn(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.NameColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)

    def test_renderCell(self):
        item = Mock()
        item.__name__ = "ItemName"
        context = Mock()
        tbl = Mock()
        tbl.selectedItems = []
        col = column.NameColumn(context, TestRequest(), tbl)
        self.assertEqual(col.renderCell(item), "ItemName")

        item.__name__ = '14" <monitor>'
        self.assertEqual(col.renderCell(item), "14&quot; &lt;monitor&gt;")


class TestRadioColumn(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.RadioColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)

    def test_renderCell(self):
        item = Mock()
        item.__name__ = "ItemName"
        context = Mock()
        tbl = Mock()
        tbl.selectedItems = []
        col = column.RadioColumn(context, TestRequest(), tbl)
        col.id = "foo&bar"
        out = col.renderCell(item)
        self.assertEqual(
            out,
            '<input type="radio" class="radio-widget" '
            'name="foo&amp;bar-selectedItem" value="ItemName" />',
        )

        tbl.selectedItems = [item]
        out = col.renderCell(item)
        self.assertEqual(
            out,
            '<input type="radio" class="radio-widget" '
            'name="foo&amp;bar-selectedItem" value="ItemName" '
            'checked="checked" />',
        )

        # now let's see how to-be-encoded item __name__ works
        tbl.selectedItems = []
        item.__name__ = '14" <monitor>'
        out = col.renderCell(item)
        self.assertEqual(
            out,
            '<input type="radio" class="radio-widget" '
            'name="foo&amp;bar-selectedItem" '
            'value="14&quot; &lt;monitor&gt;" />',
        )


class TestCheckBoxColumn(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.CheckBoxColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)

    def test_renderCell(self):
        item = Mock()
        item.__name__ = "ItemName"
        context = Mock()
        tbl = Mock()
        tbl.selectedItems = []
        col = column.CheckBoxColumn(context, TestRequest(), tbl)
        col.id = "foo&bar"
        out = col.renderCell(item)
        self.assertEqual(
            out,
            '<input type="checkbox" class="checkbox-widget" '
            'name="foo&amp;bar-selectedItems" value="ItemName" />',
        )

        tbl.selectedItems = [item]
        out = col.renderCell(item)
        self.assertEqual(
            out,
            '<input type="checkbox" class="checkbox-widget" '
            'name="foo&amp;bar-selectedItems" value="ItemName" '
            'checked="checked" />',
        )

        # now let's see how to-be-encoded item __name__ works
        tbl.selectedItems = []
        item.__name__ = '14" <monitor>'
        out = col.renderCell(item)
        self.assertEqual(
            out,
            '<input type="checkbox" class="checkbox-widget" '
            'name="foo&amp;bar-selectedItems" '
            'value="14&quot; &lt;monitor&gt;" />',
        )


class TestLinkColumn(InterfaceBaseTest, unittest.TestCase):
    def setUp(self):
        self.root = siteSetUp(True)
        self.container = testing.Container()
        self.root["container"] = self.container
        zope.traversing.testing.setUp()

    def tearDown(self):
        siteTearDown()

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.LinkColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)

    def test_getLinkContent(self):
        item = Mock()
        item.__name__ = "ItemName"
        context = Mock()
        tbl = Mock()
        col = column.LinkColumn(context, TestRequest(), tbl)
        self.assertEqual(col.getLinkContent(item), "ItemName")

        item.__name__ = '14" <monitor>'
        self.assertEqual(col.getLinkContent(item), '14" <monitor>')

        col.linkContent = "Solo"
        self.assertEqual(col.getLinkContent(item), "Solo")

        col.linkContent = '32" <TV>'
        self.assertEqual(col.getLinkContent(item), '32" <TV>')

    def test_getLinkURL(self):
        item = testing.Content("foobar", 42)
        self.container["fourty-two"] = item
        request = TestRequest()
        tbl = table.Table(None, request)
        col = column.LinkColumn(self.root, request, tbl)
        self.assertEqual(
            col.getLinkURL(item),
            "http://127.0.0.1/container/fourty-two"
        )
        col.linkName = 'index.html'
        self.assertEqual(
            col.getLinkURL(item),
            "http://127.0.0.1/container/fourty-two/index.html"
        )

        item = testing.Content("another bar", 2)
        self.container['14" <monitor>'] = item
        self.assertEqual(
            col.getLinkURL(item),
            "http://127.0.0.1/container/14%22%20%3Cmonitor%3E/index.html"
        )

    def test_renderCell(self):
        item = testing.Content("foobar", 42)
        self.container["fourty-two"] = item
        request = TestRequest()
        tbl = table.Table(None, request)
        col = column.LinkColumn(self.root, request, tbl)
        self.assertEqual(
            col.renderCell(item),
            '<a href="http://127.0.0.1/container/fourty-two">fourty-two</a>'
        )

        item = testing.Content("another bar", 2)
        self.container['14" <monitor>'] = item
        self.assertEqual(
            col.renderCell(item),
            '<a href="http://127.0.0.1/container/14%22%20%3Cmonitor%3E">'
            "14&quot; &lt;monitor&gt;</a>"
        )


class TestEMailColumn(InterfaceBaseTest, unittest.TestCase):
    def setUp(self):
        self.root = siteSetUp(True)
        self.container = testing.Container()
        self.root["container"] = self.container
        zope.traversing.testing.setUp()

    def tearDown(self):
        siteTearDown()

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.EMailColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)

    def test_getLinkContent(self):
        item = Mock()
        item.__name__ = "ItemName"
        item.title = "fooTitle"
        context = Mock()
        tbl = Mock()
        col = column.EMailColumn(context, TestRequest(), tbl)
        col.attrName = "title"
        self.assertEqual(col.getLinkContent(item), "fooTitle")

        item.title = '14" <monitor>'
        self.assertEqual(col.getLinkContent(item), '14" <monitor>')

        col.linkContent = "Solo"
        self.assertEqual(col.getLinkContent(item), "Solo")

        col.linkContent = '32" <TV>'
        self.assertEqual(col.getLinkContent(item), '32" <TV>')

    def test_renderCell(self):
        item = testing.Content("", 42)
        self.container["fourty-two"] = item
        request = TestRequest()
        tbl = table.Table(None, request)
        col = column.EMailColumn(self.root, request, tbl)
        col.attrName = "title"
        self.assertEqual(col.renderCell(item), "")

        item.title = "foo@mail.com"
        self.assertEqual(
            col.renderCell(item),
            '<a href="mailto:foo@mail.com">foo@mail.com</a>',
        )

        # according to RFC 5321 an email addr can contain <>&
        item = testing.Content("John Doe <john@mail.com>", 2)
        self.container["john"] = item
        self.assertEqual(
            col.renderCell(item),
            '<a href="mailto:John Doe &lt;john@mail.com&gt;">'
            "John Doe &lt;john@mail.com&gt;</a>",
        )


# batch
class TestBatchProvider(InterfaceBaseTest, unittest.TestCase):
    def getTestInterface(self):
        return interfaces.IBatchProvider

    def getTestClass(self):
        return batch.BatchProvider

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        t.rows = Batch([])
        return ({}, TestRequest(), t)


class Mock:
    pass


def test_suite():
    checker = RENormalizing(
        (
            (re.compile("u'(.*)'"), "'\\1'"),
            (re.compile('u"(.*)"'), '"\\1"'),
            (
                re.compile("zope.security.interfaces.Unauthorized"),
                "Unauthorized",
            ),
        )
    )

    return unittest.TestSuite(
        (
            doctest.DocFileSuite(
                "README.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            doctest.DocFileSuite(
                "sequence.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            doctest.DocFileSuite(
                "sort.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            doctest.DocFileSuite(
                "batch.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE
                | doctest.ELLIPSIS
                | doctest.REPORT_UDIFF,
            ),
            doctest.DocFileSuite(
                "miscellaneous.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            doctest.DocFileSuite(
                "column.rst",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                checker=checker,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
            unittest.defaultTestLoader.loadTestsFromName(__name__),
        )
    )
