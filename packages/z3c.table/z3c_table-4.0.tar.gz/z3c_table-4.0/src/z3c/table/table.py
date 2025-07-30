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
from xml.sax.saxutils import quoteattr

import zope.component
import zope.interface
import zope.location
from z3c.batching.batch import Batch
from z3c.batching.interfaces import IBatch

from z3c.table import column
from z3c.table import interfaces


def getWeight(column):
    try:
        return int(column.weight)
    except AttributeError:
        return 0


def getSortMethod(idx):
    def getSortKey(item):
        sublist = item[idx]

        def getColumnSortKey(sublist):
            return sublist[1].getSortKey(sublist[0])

        return getColumnSortKey(sublist)

    return getSortKey


def getCurrentSortID(sortOn):
    # this may return a string 'id-name-idx' if coming from request,
    # otherwise in Table class it is intialised as a integer string
    try:
        currentSortID = int(sortOn)
    except ValueError:
        currentSortID = sortOn.rsplit("-", 1)[-1]
    try:
        currentSortID = int(currentSortID)
    except ValueError:
        return None
    return currentSortID


def nameColumn(column, name):
    """Give a column a __name__."""
    column.__name__ = name
    return column


@zope.interface.implementer(interfaces.ITable)
class Table(zope.location.Location):
    """Generic usable table implementation."""

    # customize this part if needed
    prefix = "table"

    # css classes
    cssClasses = {}
    # additional (row) css
    cssClassEven = ""
    cssClassOdd = ""
    cssClassSelected = ""
    # css to show sorting, set to None to turn off
    cssClassSortedOn = "sorted-on"

    # sort attributes
    sortOn = 0
    sortOrder = "ascending"
    reverseSortOrderNames = ["descending", "reverse", "down"]

    # batch attributes
    batchProviderName = "batch"
    batchStart = 0
    batchSize = 50
    startBatchingAt = 50

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context
        # private variables will be set in update call
        self.batchProvider = None
        self.columnCounter = 0
        self.columnIndexById = {}
        self.columnByName = {}
        self.columns = None
        self.rows = []
        self.selectedItems = []

    def initColumns(self):
        # setup columns
        self.columns = self.setUpColumns()
        # order columns
        self.orderColumns()

    @property
    def values(self):
        adapter = zope.component.getMultiAdapter(
            (self.context, self.request, self), interfaces.IValues
        )
        return adapter.values

    # CSS helpers

    def getCSSHighlightClass(self, column, item, cssClass):
        """Provide a highlight option for any cell"""
        return cssClass

    def getCSSSortClass(self, column, cssClass):
        """Add CSS class based on current sorting"""
        if self.cssClassSortedOn and self.sortOn is not None:
            currentSortID = getCurrentSortID(self.sortOn)
            sortID = column.id.rsplit("-", 1)[-1]

            if int(sortID) == currentSortID:
                klass = self.cssClassSortedOn + " " + self.sortOrder
                if cssClass:
                    cssClass += " " + klass
                else:
                    cssClass = klass
        return cssClass

    def getCSSClass(self, element, cssClass=None):
        """Add CSS class based on HTML tag, make a `class=` attribute"""
        klass = self.cssClasses.get(element)
        if klass and cssClass:
            klass = f"{cssClass} {klass}"
        elif cssClass:
            klass = cssClass
        return " class=%s" % quoteattr(klass) if klass else ""

    # setup

    def setUpColumns(self):
        cols = list(
            zope.component.getAdapters(
                (self.context, self.request, self), interfaces.IColumn
            )
        )
        # use the adapter name as column name
        return [nameColumn(col, name) for name, col in cols]

    def updateColumns(self):
        for col in self.columns:
            col.update()

    def orderColumns(self):
        self.columnCounter = 0
        self.columns = sorted(self.columns, key=getWeight)
        for col in self.columns:
            self.columnByName[col.__name__] = col
            idx = self.columnCounter
            col.id = f"{self.prefix}-{col.__name__}-{idx}"
            self.columnIndexById[col.id] = idx
            self.columnCounter += 1

    def setUpRow(self, item):
        cols = []
        append = cols.append
        colspanCounter = 0
        countdown = len(self.columns)
        for col in self.columns:
            countdown -= 1
            colspan = 0
            if colspanCounter == 0:
                colspan = colspanCounter = col.getColspan(item)
                # adjust colspan because we define 0, 2, 3, etc.
                if colspanCounter > 0:
                    colspanCounter -= 1

            if colspan == 0 and colspanCounter > 0:
                # override col if colspan is 0 and colspan coutner not 0
                colspanCounter -= 1
                colspan = 0
                # now we are ready to setup dummy colspan cells
                col = column.NoneCell(self.context, self.request, self)

            # we reached the end of the table and have still colspan
            if (countdown - colspan) < 0:
                raise ValueError(
                    "Colspan for column '%s' is larger than the table." % col
                )

            append((item, col, colspan))
        return cols

    def setUpRows(self):
        return [self.setUpRow(item) for item in self.values]

    # sort

    def getSortOn(self):
        """Returns sort on column id."""
        return self.request.get(self.prefix + "-sortOn", self.sortOn)

    def getSortOrder(self):
        """Returns sort order criteria."""
        return self.request.get(self.prefix + "-sortOrder", self.sortOrder)

    def sortRows(self):
        if self.sortOn is not None and self.rows and self.columns:
            sortOnIdx = self.columnIndexById.get(self.sortOn, 0)
            sortKeyGetter = getSortMethod(sortOnIdx)
            rows = sorted(self.rows, key=sortKeyGetter)
            if self.sortOrder in self.reverseSortOrderNames:
                rows.reverse()
            self.rows = rows

    # batch

    def getBatchSize(self):
        try:
            newSize = int(
                self.request.get(self.prefix + "-batchSize", self.batchSize)
            )
        except ValueError:
            newSize = self.batchSize
        if newSize < 1:
            newSize = self.batchSize
        return newSize

    def getBatchStart(self):
        try:
            return int(
                self.request.get(self.prefix + "-batchStart", self.batchStart)
            )
        except ValueError:
            return self.batchStart

    def batchRows(self):
        length = len(self.rows)
        if length > self.startBatchingAt:
            if self.batchStart >= length:
                self.batchStart = length - self.batchSize
            if self.batchStart < 0:
                self.batchStart = 0

            self.rows = Batch(
                self.rows, start=self.batchStart, size=self.batchSize
            )

    def updateBatch(self):
        if IBatch.providedBy(self.rows):
            self.batchProvider = zope.component.getMultiAdapter(
                (self.context, self.request, self),
                interfaces.IBatchProvider,
                name=self.batchProviderName,
            )
            self.batchProvider.update()

    def isSelectedRow(self, row):
        item, col, colspan = row[0]
        if item in self.selectedItems:
            return True
        return False

    # render

    def renderBatch(self):
        if self.batchProvider is None:
            return ""
        return self.batchProvider.render()

    def renderTable(self):
        if self.columns:
            cssClass = self.getCSSClass("table")
            head = self.renderHead()
            body = self.renderBody()
            return f"<table{cssClass}>{head}{body}\n</table>"
        return ""

    def renderHead(self):
        cssClass = self.getCSSClass("thead")
        rStr = self.renderHeadRow()
        return f"\n  <thead{cssClass}>{rStr}\n  </thead>"

    def renderHeadRow(self):
        cssClass = self.getCSSClass("tr")
        cells = [self.renderHeadCell(col) for col in self.columns]
        return "\n    <tr{}>{}\n    </tr>".format(cssClass, "".join(cells))

    def renderHeadCell(self, column):
        cssClass = column.cssClasses.get("th")
        cssClass = self.getCSSSortClass(column, cssClass)
        cssClass = self.getCSSClass("th", cssClass)
        return f"\n      <th{cssClass}>{column.renderHeadCell()}</th>"

    def renderBody(self):
        cssClass = self.getCSSClass("tbody")
        rStr = self.renderRows()
        return f"\n  <tbody{cssClass}>{rStr}\n  </tbody>"

    def renderRows(self):
        counter = 0
        rows = []
        cssClasses = (self.cssClassEven, self.cssClassOdd)
        append = rows.append
        for row in self.rows:
            append(self.renderRow(row, cssClasses[counter % 2]))
            counter += 1
        return "".join(rows)

    def renderRow(self, row, cssClass=None):
        isSelected = self.isSelectedRow(row)
        if isSelected and self.cssClassSelected and cssClass:
            cssClass = f"{self.cssClassSelected} {cssClass}"
        elif isSelected and self.cssClassSelected:
            cssClass = self.cssClassSelected
        cssClass = self.getCSSClass("tr", cssClass)
        cells = [
            self.renderCell(item, col, colspan) for item, col, colspan in row
        ]
        return "\n    <tr{}>{}\n    </tr>".format(cssClass, "".join(cells))

    def renderCell(self, item, column, colspan=0):
        if interfaces.INoneCell.providedBy(column):
            return ""
        cssClass = column.cssClasses.get("td")
        cssClass = self.getCSSHighlightClass(column, item, cssClass)
        cssClass = self.getCSSSortClass(column, cssClass)
        cssClass = self.getCSSClass("td", cssClass)
        colspanStr = ' colspan="%s"' % colspan if colspan else ""
        return "\n      <td{}{}>{}</td>".format(
            cssClass,
            colspanStr,
            column.renderCell(item),
        )

    def update(self):
        # reset values
        self.columnCounter = 0
        self.columnByIndex = {}
        self.selectedItems = []

        # use batch values from request or the existing ones
        self.batchSize = self.getBatchSize()
        self.batchStart = self.getBatchStart()
        # use sorting values from request or the existing ones
        self.sortOn = self.getSortOn()
        self.sortOrder = self.getSortOrder()

        # initialize columns
        self.initColumns()

        # update columns
        self.updateColumns()

        # setup headers based on columns
        self.rows = self.setUpRows()

        # sort items on columns
        self.sortRows()

        # batch sorted rows
        self.batchRows()

        self.updateBatch()

    def render(self):

        # allow to use a template for rendering the table, this will allow
        # to position the batch before and after the table

        return self.renderTable()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__name__!r}>"


@zope.interface.implementer(interfaces.ISequenceTable)
class SequenceTable(Table):
    """Sequence table adapts a sequence as context.

    This table can be used for adapting a z3c.indexer.search.ResultSet or
    z3c.batching.batch.Batch instance as context. Batch which wraps a
    ResultSet sequence.
    """
