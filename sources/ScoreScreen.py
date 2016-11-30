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

class ScoreEntry(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ScoreEntry, self).__init__(parent)
        self.initUI()

    def initUI(self):
        
        self.rankLbl = QtGui.QLabel(self)
        self.rankLbl.setMaximumWidth(20)
        self.nickLbl = QtGui.QLabel(self)
        self.hitLbl = QtGui.QLabel(self)
        self.pointLbl = QtGui.QLabel(self)


        container = QtGui.QHBoxLayout()
        container.addWidget(self.rankLbl)
        container.addWidget(self.nickLbl)
        container.addWidget(self.hitLbl)
        container.addWidget(self.pointLbl)

        self.setLayout(container)
        self.setMaximumHeight(35)

    def setEntryData(self, data):
        self.rankLbl.setText(str(data['Rank']))
        self.nickLbl.setText(unicode(data['Nickname']))
        self.hitLbl.setText(str(data['HIT']))
        self.pointLbl.setText(str(data['Point']))

#************************************************************************************************************************************************************#

class ScorePage(QtGui.QWidget):
    def __init__(self, data, parent=None):
        super(ScorePage, self).__init__(parent)
        self.initUI(data)

    def initUI(self, data):
        self.data = data
        
        self.rankLbl = QtGui.QLabel('#', self)
        self.rankLbl.setObjectName('Header')
        self.rankLbl.setMaximumWidth(20)
        self.nickLbl = QtGui.QLabel('Nickname', self)
        self.nickLbl.setObjectName('Header')
        self.hitLbl = QtGui.QLabel('HITS', self)
        self.hitLbl.setObjectName('Header')
        self.pointLbl = QtGui.QLabel('Points', self)
        self.pointLbl.setObjectName('Header')

        headerContainer = QtGui.QHBoxLayout()
        headerContainer.addWidget(self.rankLbl)
        headerContainer.addWidget(self.nickLbl)
        headerContainer.addWidget(self.hitLbl)
        headerContainer.addWidget(self.pointLbl)
        headerContainer.setContentsMargins(10, 0, 10, 0)
        
        
        
        self.scoreGrid = QtGui.QVBoxLayout()
        self.scoreGrid.setSpacing(0)
        self.scoreGrid.addLayout(headerContainer)

        self.scoreGrid.setAlignment(QtCore.Qt.AlignTop) # align content to top
        
        self.createEntries()

        self.setLayout(self.scoreGrid)

        self.retranslateUI()

    def createEntries(self):
        """ populates the scoreGrid with ScoreEntry instances """
        for rowData in self.data:
            entry = ScoreEntry(self)
            entry.setEntryData(rowData)
            self.scoreGrid.addWidget(entry)

    
    def changeEvent(self, event):
        """ triggers retranslate ui when a language change occurs """
        super(ScorePage, self).changeEvent(event)
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUI()
        
    def retranslateUI(self):
        """ retranslate all static texts that is listed below """
        self.nickLbl.setText(self.tr('Nickname'))
        self.hitLbl.setText(self.tr('HITS'))
        self.pointLbl.setText(self.tr('Points'))
        

#************************************************************************************************************************************************************#
class ScorePager(QtGui.QWidget):

    MaxPageEntries = 8

    def __init__(self, parent=None):
        super(ScorePager, self).__init__(parent)
        self.initUI()

    def initUI(self):
        
        self.scoreData = []

        self.pager = QtGui.QStackedWidget(self)
        
        self.btnContainer = QtGui.QHBoxLayout()
        self.btnGroup = QtGui.QButtonGroup()
        self.btnGroup.setExclusive(True)    # restricts the group to have only one button checked at a time

        container = QtGui.QVBoxLayout(self)
        container.addWidget(self.pager)
        container.setAlignment(self.pager, QtCore.Qt.AlignTop)
        container.addStretch(1)
        container.addLayout(self.btnContainer)
        container.setAlignment(self.btnContainer, QtCore.Qt.AlignCenter)

        self.setLayout(container)

    def getScoreData(self):
        """ fetches and returns scores of users"""
        scoreData = []
        conn = pymssql.connect(*connString)
        cur = conn.cursor(as_dict=True)

        cur.execute("SELECT [Nickname], [Pont], [HIT] FROM [dbo].[eb_2016_user_standing] order by [Pont] desc ,[HIT] desc ")
        rank = 1
        for row in cur:
            scoreData.append({
                                'Rank' : rank,
                                'Nickname' : row['Nickname'],
                                'HIT' : row['HIT'],
                                'Point' : row['Pont'],
                            })
            rank += 1
        conn.close()
        
        return scoreData

        
    def createPageData(self, pageNum):
        """ returns the corresponding page data according to page number """
        start = pageNum * self.MaxPageEntries
        stop = start + self.MaxPageEntries
        pageData = self.scoreData[start:stop]
        return pageData

    def createPages(self):
        """ creates ScorePage widgets """
        pageNum = int(ceil(float(len(self.scoreData)) / self.MaxPageEntries)) # determine the number of pages
        for i in range(pageNum):
            data = self.createPageData(i)
            page = ScorePage(data, self)
            self.pager.addWidget(page)
            
    def deletePages(self):
        """ deletes ScorePager widgets """
        pages = []
        for i in range(self.pager.count()):
            pages.append(self.pager.widget(i))

        for page in pages:
            page.setParent(None)
            page.deleteLater()

    def createPagerButtons(self):
        """ creates control buttons to switch amongst score pages """
        pageNum =  int(ceil(float(len(self.scoreData)) / self.MaxPageEntries))
        for i in range(pageNum):
            btn = QtGui.QPushButton(str(i+1), self)
            btn.setObjectName('PagerButton')
            btn.setCheckable(True)
            btn.clicked.connect(self.switchPage)
            self.btnGroup.addButton(btn)
            self.btnContainer.addWidget(btn)

        if pageNum > 0:
            self.btnGroup.buttons()[0].setChecked(True)

        

    def deletePagerButtons(self):
        """ deletes pager buttons """
        pagerButtons = self.btnGroup.buttons()
        for button in pagerButtons:
            self.btnGroup.removeButton(button)
            button.setParent(None)
            button.deleteLater()

    def switchPage(self):
        """ switch the pager to the correspondig pager index of the pager button text"""
        index = int(self.sender().text()) - 1
        self.pager.setCurrentIndex(index)

    def reinitUI(self):
        """ reinitializes ScorePager """
        self.scoreData = self.getScoreData()
        self.deletePages()
        self.createPages()
        self.deletePagerButtons()
        self.createPagerButtons()
        

#************************************************************************************************************************************************************#

class ScoreScreen(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ScoreScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):
        
        self.backBtn = QtGui.QPushButton('Back', self)
        self.backBtn.setObjectName('BackButton')

        self.scorePager = ScorePager(self)
      
        container = QtGui.QVBoxLayout()
        container.addWidget(self.scorePager)
        
        container.addWidget(self.backBtn)
        container.setAlignment(self.backBtn, QtCore.Qt.AlignLeft)
        container.setSpacing(0)
        self.setLayout(container)

    def changeEvent(self, event):
        """ triggers retranslate ui when a language change occurs """
        super(ScoreScreen, self).changeEvent(event)
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUI()

    def retranslateUI(self):
        """ retranslate all static texts that is listed below """
        self.backBtn.setText(self.tr('Back'))

    def reinitUI(self):
        """ reinitializes ScoreScreen """
        self.scorePager.reinitUI()
#************************************************************************************************************************************************************#
        
