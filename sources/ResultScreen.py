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

class ResultEntry(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ResultEntry, self).__init__(parent)
        self.initUI()
        
    def initUI(self):

        self.dateTxt = QtGui.QLabel(self)
        
    
        self.timeTxt = QtGui.QLabel(self)
        self.timeTxt.setMaximumWidth(50)
        self.timeTxt.setMaximumHeight(50)
    
    
        self.homeBtn = QtGui.QPushButton("Home")
        self.homeBtn.setIcon(QtGui.QIcon('flags/default.png'))
        self.homeBtn.setMinimumWidth(200)

        self.homeTxt = QtGui.QLabel(self)
    
        self.visitorBtn = QtGui.QPushButton("Visitor")
        self.visitorBtn.setIcon(QtGui.QIcon('flags/default.png'))
        self.visitorBtn.setMinimumWidth(200)

        self.visitorTxt = QtGui.QLabel(self)

        colon = QtGui.QLabel(':')
        colon.setMaximumWidth(20)

        container = QtGui.QHBoxLayout()
        container.addWidget(self.dateTxt)
        container.addWidget(self.timeTxt)
        container.addWidget(self.homeBtn)
        container.addWidget(self.homeTxt)
        container.addWidget(colon)
        container.addWidget(self.visitorTxt)
        container.addWidget(self.visitorBtn)
        
        self.setMaximumHeight(40) 
        self.setLayout(container)

    def setHomeBtnText(self, country):
        """ sets home button text and icon """ 
        self.homeBtn.setText(country)
        icon = shared.getCountryFlagPath(country)
        self.homeBtn.setIcon(QtGui.QIcon(icon))
        
    def setVisitorBtnText(self, country):
        """ sets visitor button text and icon """
        self.visitorBtn.setText(country)
        icon = shared.getCountryFlagPath(country)
        self.visitorBtn.setIcon(QtGui.QIcon(icon))

    def setEntryData(self, data):
        """ initializes the entry from data """
        self.dateTxt.setText(data['Date'])
        self.timeTxt.setText(data['Time'])
        self.setHomeBtnText(data['Home'])
        self.homeTxt.setText(str(data['H-Gol']))
        self.visitorTxt.setText(str(data['V-Gol']))
        self.setVisitorBtnText(data['Visitor'])
    
#************************************************************************************************************************************************************#
        
class ResultPage(QtGui.QWidget):
    def __init__(self, data, parent=None):
        super(ResultPage, self).__init__(parent)
        self.initUI(data)

    def initUI(self, data):
        self.pageData = data

        self.resultGrid = QtGui.QVBoxLayout()
        self.resultGrid.setSpacing(0)
        self.resultGrid.setAlignment(QtCore.Qt.AlignTop) # align content to top
        self.entryGroup = []        # array to contain ResultEntry instances
        self.setGridData()

        self.setLayout(self.resultGrid)

    def setGridData(self):
        """ row by row from pageData, creates the result entries, and appends them to the entrygroup
            and adds them to the result grid """
        for dataRow in self.pageData:
            entry = ResultEntry(self)
            entry.setEntryData(dataRow)
            self.entryGroup.append(entry)
            self.resultGrid.addWidget(entry)
        

    def updatePageData(self, data):
        """ updates the pageData array """
        self.pageData = data

    def updateGridData(self):
        """ row by row from pageData, reloads the result entries' entry datas """
        row = 0
        for entry in self.entryGroup:
            entry.setEntryData(self.pageData[row])
            row += 1

#************************************************************************************************************************************************************#

class ResultPager(QtGui.QWidget):
    
    MaxPageEntries = 8

    def __init__(self, parent=None):
        super(ResultPager, self).__init__(parent)
        self.initUI()

    def initUI(self):

        self.resultData = []

        self.pager = QtGui.QStackedWidget(self)

        self.btnContainer = QtGui.QHBoxLayout()
        self.btnGroup = QtGui.QButtonGroup()
        self.btnGroup.setExclusive(True)    # restricts the group to have only one button checked at a time

        container = QtGui.QVBoxLayout(self)
        container.addWidget(self.pager)
        container.setAlignment(self.pager, QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        container.addStretch(1)
        container.addLayout(self.btnContainer)
        container.setAlignment(self.btnContainer, QtCore.Qt.AlignCenter)

        self.setLayout(container)

    def getResultData(self):
        """ fetches and returns match results """
        resultData = []
        
        conn = pymssql.connect(*connString)
        cur = conn.cursor(as_dict=True)
        lang = shared.getCfgLang()
        cur.callproc('eb_2016_get_match_results', (lang,))
        for row in cur:
            resultData.append(
                                {'Date' : row['Date'],
                                 'Time' : row['Time'],
                                 'Home' : row['Home'],
                                 'H-Gol' : row['H-Gol'],
                                 'V-Gol' : row['V-Gol'],
                                 'Visitor' : row['Visitor']
                                 }
                                )
        conn.close()
        return resultData
        
        
    def createPageData(self, pageNum):
        """ returns the corresponding page data according to page number """
        start = pageNum * self.MaxPageEntries
        stop = start + self.MaxPageEntries
        pageData = self.resultData[start:stop]
        return pageData

    def createPages(self):
        """ creates ResultPage widgets """
        pageNum = int(ceil(float(len(self.resultData)) / self.MaxPageEntries))
        for i in range(pageNum): 
            data = self.createPageData(i)
            page = ResultPage(data, self)
            self.pager.addWidget(page)

    def deletePages(self):
        """ deletes ResultPage widgets from pager """
        pages = []
        for i in range(self.pager.count()):
            pages.append(self.pager.widget(i))

        for page in pages:
            page.setParent(None)
            page.deleteLater()

    def updatePages(self):
        """ updates the pages with new data """
        for i in range(self.pager.count()):
            page = self.pager.widget(i)
            data = self.createPageData(i)
            page.updatePageData(data)
            page.updateGridData()

    def deletePagerButtons(self):
        """ deletes pager control buttons from btnGroup """
        pagerButtons = self.btnGroup.buttons()
        for button in pagerButtons:
            self.btnGroup.removeButton(button)
            button.setParent(None)
            button.deleteLater()

    def createPagerButtons(self):
        """ creates control buttons to switch amongst score pages """
        pageNum =  int(ceil(float(len(self.resultData)) / self.MaxPageEntries))
        for i in range(pageNum):
            btn = QtGui.QPushButton(str(i+1), self)
            btn.setObjectName('PagerButton')
            btn.setCheckable(True)
            btn.clicked.connect(self.switchPage)
            self.btnGroup.addButton(btn)
            self.btnContainer.addWidget(btn)


        if pageNum > 0:
            self.btnGroup.buttons()[0].setChecked(True) # checks the first button in the group

    def switchPage(self):
        """ switches the pager to the correspondig pager index of the pager button text"""
        index = int(self.sender().text()) - 1
        self.pager.setCurrentIndex(index)

    def changeEvent(self, event):
        """ triggers retranslate ui when a language change occurs """
        super(ResultPager, self).changeEvent(event)
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUI()

    def retranslateUI(self):
        """ retranslate all static texts that is listed below """
        self.resultData = self.getResultData()
        self.updatePages()

    def reinitUI(self):
        """ reinitialize the pager """
        self.resultData = self.getResultData()
        self.deletePages()
        self.createPages()
        self.deletePagerButtons()
        self.createPagerButtons()
        
#************************************************************************************************************************************************************#

class ResultScreen(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ResultScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):      
        self.backBtn = QtGui.QPushButton('Back', self)
        self.backBtn.setObjectName('BackButton')

        self.resultPager = ResultPager(self)
      
        container = QtGui.QVBoxLayout()
        container.addWidget(self.resultPager)
        
        container.addWidget(self.backBtn)
        container.setAlignment(self.backBtn, QtCore.Qt.AlignLeft)
        self.setLayout(container)

    def changeEvent(self, event):
        """ triggers retranslate ui when a language change occurs """
        super(ResultScreen, self).changeEvent(event)
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUI()      

    def retranslateUI(self):
        """ retranslate all static texts that is listed below """
        self.backBtn.setText(self.tr('Back'))

    def reinitUI(self):
        """ reinitialize result screen """
        self.resultPager.reinitUI()

#************************************************************************************************************************************************************#        
