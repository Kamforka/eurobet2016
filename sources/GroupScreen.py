#!/usr/bin/python
#-*- coding: utf-8-*-

#dialogs.py

''' PyQt imports '''
import sys
from PyQt4 import QtGui, QtCore

''' Database Imports '''
import pymssql
from credentials import connString

''' Shared functions imports '''
import shared

from math import ceil

#************************************************************************************************************************************************************#

class GroupGrid(QtGui.QWidget):
    """ Creates a table with a header to display group standings """
    def __init__(self, data, parent=None):
        super(GroupGrid, self).__init__(parent)
        self.initUI(data)

    def initUI(self, data):

        ''' No need to create retranslateUI method because
            on languagechange event groupscreen always reinitialize
            the group grid layout '''
        self.data = data
    
        rows = len(self.data)
        cols = len(self.data[0])
    
        
        self.header = QtGui.QLabel('Group X', self)
        tableHeaders = [self.tr('Country'), self.tr('W'), self.tr('D'), self.tr('L'), self.tr('GD'), self.tr('Points')]

        self.table = QtGui.QTableWidget(self)
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed) #disable cell adjusting

        self.setTableData()
        
        self.table.setHorizontalHeaderLabels(tableHeaders)
        self.table.resizeColumnsToContents()
        self.table.verticalHeader().setVisible(False)
        self.table.setCornerButtonEnabled(False)
        self.table.setShowGrid(False)
        
        self.table.setColumnWidth(0, 135)   # Manual width correction for the Country column
        self.table.setColumnWidth(5, 52)    # Manual width correction for the Points column
        self.table.resizeRowsToContents()
        
        container = QtGui.QVBoxLayout()
        container.addWidget(self.header)
        container.setAlignment(self.header, QtCore.Qt.AlignCenter)
        container.addWidget(self.table)

        self.setLayout(container)

    def setGroupHeader(self, group):
        """ sets the widget header label to the specified group text """
        headerTxt = self.tr('Group ') + group
        self.header.setText(headerTxt)

    def setTableData(self):
        """ populates the table from self.data """
        for x in range(len(self.data)):
            for y in range(len(self.data[x])):
                
                if y == 0:
                    ''' appending icons to the countries '''
                    flagPath = shared.getCountryFlagPath(self.data[x][y])
                    icon = QtGui.QIcon(flagPath)
                    item = QtGui.QTableWidgetItem(icon, self.data[x][y])
                else:
                    ''' otherwise just create the item '''
                    item = QtGui.QTableWidgetItem(str(self.data[x][y]))
                    item.setTextAlignment(QtCore.Qt.AlignCenter) # set text alignment to centered
                    
                item.setFlags(QtCore.Qt.ItemIsEnabled)  # this flag sets the cell item read only
                self.table.setItem(x, y, item)

#************************************************************************************************************************************************************#

class GroupScreen(QtGui.QWidget):
        
    def __init__(self, parent=None):
        super(GroupScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):
        
        self.groupGrids = []    # to contain group grid instances
        self.grid = QtGui.QGridLayout()

        self.createGroupTables()

        self.backBtn = QtGui.QPushButton('Back', self)
        self.backBtn.setObjectName('BackButton')


        container = QtGui.QVBoxLayout(self)
        
        container.addLayout(self.grid)
        container.addWidget(self.backBtn)
        container.setAlignment(self.backBtn, QtCore.Qt.AlignLeft)
        self.setLayout(container)

        self.retranslateUI()

    def clearGroupTables(self):
        """ removes every group grid from the grid container
            and then deletes them, and empties the groupGrids array """
        
        for groupGrid in self.groupGrids:
            self.grid.removeWidget(groupGrid)
            groupGrid.setParent(None)
            groupGrid.deleteLater()
        self.groupGrids = []
        

    def createGroupTables(self):
        """ populates the grid with group grids """
        ROWS = 2
        COLS = 3
        groupLbls = ['A', 'B', 'C', 'D', 'E', 'F']
        
        lang = shared.getCfgCountryCode()
        
        ''' create group grids '''
        for groupLbl in groupLbls:
            data = self.getGroupData(groupLbl, lang)
            group = GroupGrid(data, self)
            group.setGroupHeader(groupLbl)
            self.groupGrids.append(group)

        ''' create positions for group grids '''
        positions = [(x, y) for x in range(ROWS) for y in range(COLS)]
        
        for group, position in zip(self.groupGrids, positions):
             self.grid.addWidget(group, *position)

    def getGroupData(self, group, lang='EN'):
        """ fetches then returns the specified group's tabelle data """
        groupData = []
        
        conn = pymssql.connect(*connString)
        cur = conn.cursor(as_dict=True)

        cur.callproc('eb_2016_get_group', (group, lang,))

        for row in cur:
            countryData = [row[lang], row['W'], row['D'], row['L'], row['GD'], row['Points']]
            groupData.append(countryData)
        conn.close()

        return groupData

    def changeEvent(self, event):
        """ triggers retranslate ui when a language change occurs """
        super(GroupScreen, self).changeEvent(event)
        if event.type() == QtCore.QEvent.LanguageChange:
            self.clearGroupTables()
            self.createGroupTables()
            self.retranslateUI()

    def retranslateUI(self):
        """ retranslate all static texts that is listed below """
        self.backBtn.setText(self.tr('Back'))
