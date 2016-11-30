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
class BracketPainter(QtGui.QWidget):

    def __init__(self, parent=None):
        super(BracketPainter, self).__init__(parent)
        self.initUI()

    def initUI(self):
        
        container = QtGui.QBoxLayout(QtGui.QBoxLayout.BottomToTop)
        self.setLayout(container)

    def getRound16Data(self):
        """ fetches and returns detail of matches for round 16 """

        round16Data = []
        lang = shared.getCfgCountryCode()
        conn = pymssql.connect(*connString)
        with conn:
            cur = conn.cursor(as_dict=True)
            cur.callproc('eb_2016_get_round16_matches', (lang,))

            for row in cur:
                round16Data.append({
                    'id' : unicode(row['ID']),
                    'Date' : row['Date'],
                    'Time' : row['Time'],
                    'Home' : row['Home'],
                    'H-Goal' : '-' if unicode(row['H-Gol']) == 'None' else unicode(row['H-Gol']),
                    'H-Pen' : '-' if unicode(row['H-Pen']) == 'None' else unicode(row['H-Pen']),
                    'Visitor' : row['Visitor'],
                    'V-Goal' : '-' if unicode(row['V-Gol']) == 'None' else unicode(row['V-Gol']),
                    'V-Pen' : '-' if unicode(row['V-Pen']) == 'None' else unicode(row['V-Pen']),
                    })
                
        return round16Data

    def getQuarterData(self):
        """ fetches and returns detail of matches for quarters """

        quarterData = []
        lang = shared.getCfgCountryCode()

        conn = pymssql.connect(*connString)
        with conn:
            cur = conn.cursor(as_dict=True)
            cur.callproc('eb_2016_get_quarter_matches', (lang,))

            for row in cur:
                quarterData.append({
                    'id' : unicode(row['ID']),
                    'Date' : row['Date'],
                    'Time' : row['Time'],
                    'Home' : row['Home'],
                    'H-Goal' : '-' if unicode(row['H-Gol']) == 'None' else unicode(row['H-Gol']),
                    'H-Pen' : '-' if unicode(row['H-Pen']) == 'None' else unicode(row['H-Pen']),
                    'Visitor' : row['Visitor'],
                    'V-Goal' : '-' if unicode(row['V-Gol']) == 'None' else unicode(row['V-Gol']),
                    'V-Pen' : '-' if unicode(row['V-Pen']) == 'None' else unicode(row['V-Pen']),
                    })
                
        return quarterData

    def getSemiData(self):
        """ fetches and returns detail of matches for semis """

        semiData = []
        lang = shared.getCfgCountryCode()
        
        conn = pymssql.connect(*connString)
        with conn:
            cur = conn.cursor(as_dict=True)
            cur.callproc('eb_2016_get_semi_matches', (lang,))

            for row in cur:
                semiData.append({
                    'id' : unicode(row['ID']),
                    'Date' : row['Date'],
                    'Time' : row['Time'],
                    'Home' : row['Home'],
                    'H-Goal' : '-' if unicode(row['H-Gol']) == 'None' else unicode(row['H-Gol']),
                    'H-Pen' : '-' if unicode(row['H-Pen']) == 'None' else unicode(row['H-Pen']),
                    'Visitor' : row['Visitor'],
                    'V-Goal' : '-' if unicode(row['V-Gol']) == 'None' else unicode(row['V-Gol']),
                    'V-Pen' : '-' if unicode(row['V-Pen']) == 'None' else unicode(row['V-Pen']),
                    })
                
        return semiData

    def getFinalData(self):
        """ fetches and returns detail of final match """
        finalData = []
        lang = shared.getCfgCountryCode()
        conn = pymssql.connect(*connString)
        with conn:
            cur = conn.cursor(as_dict=True)
            cur.callproc('eb_2016_get_final_match', (lang,))

            for row in cur:
                finalData.append({
                    'id' : unicode(row['ID']),
                    'Date' : row['Date'],
                    'Time' : row['Time'],
                    'Home' : row['Home'],
                    'H-Goal' : '-' if unicode(row['H-Gol']) == 'None' else unicode(row['H-Gol']),
                    'H-Pen' : '-' if unicode(row['H-Pen']) == 'None' else unicode(row['H-Pen']),
                    'Visitor' : row['Visitor'],
                    'V-Goal' : '-' if unicode(row['V-Gol']) == 'None' else unicode(row['V-Gol']),
                    'V-Pen' : '-' if unicode(row['V-Pen']) == 'None' else unicode(row['V-Pen']),
                    })
                
        return finalData

    def paintEvent(self, e):
        
        xOffset = 250 # horizontal spacing between round columns

        bracketWidth = 180 # widthx of a single bracket
        bracketHeight = 30 # height of a single bracket 
        
        roundX = 50        # starting x coordinate for the round 16 brackets
        roundY = 10        # starting y coordinate for the round 16 brackets
        roundOffset = 50   # vertical spacing of the brackets
        roundCount = 8     # number of brackets
        data = []
        roundData = self.getRound16Data()
        
        self.drawBrackets(roundData, roundX, roundY, roundOffset, roundCount, bracketWidth, bracketHeight)
        self.drawBranches(roundX, roundY, xOffset, roundOffset, bracketWidth, bracketHeight, roundCount/2)

        quarterX = roundX + xOffset 
        quarterY = roundY + roundOffset/2
        quarterOffset = roundOffset * 2
        quarterCount = roundCount / 2
        quarterData = self.getQuarterData()
        
        self.drawBrackets(quarterData, quarterX, quarterY, quarterOffset, quarterCount, bracketWidth, bracketHeight)
        self.drawBranches(quarterX, quarterY, xOffset, quarterOffset, bracketWidth, bracketHeight, quarterCount/2)

        semiX = quarterX + xOffset
        semiY = quarterY + quarterOffset/2
        semiOffset = quarterOffset * 2
        semiCount = quarterCount / 2
        semiData = self.getSemiData()
        
        self.drawBrackets(semiData, semiX, semiY, semiOffset, semiCount, bracketWidth, bracketHeight)
        self.drawBranches(semiX, semiY, xOffset, semiOffset, bracketWidth, bracketHeight, semiCount/2)

        finalX = semiX + xOffset
        finalY = semiY + semiOffset/2
        finalOffset = semiOffset * 2
        finalCount = semiCount / 2
        finalData = self.getFinalData()

        self.drawBrackets(finalData, finalX, finalY, finalOffset, finalCount, bracketWidth, bracketHeight)        

    def drawBrackets(self, datas, x0=50, y0=50, offset=50, count = 8, width=160, height=30):
        """ draws brackets of the specified count, and fill them up with data """

        data = {
                    'id' : '10',
                    'Home' : 'Home',
                    'H-Goal' : '-',
                    'H-Pen' : '-',
                    'Visitor' : 'Visitor',
                    'V-Goal' : '-',
                    'V-Pen' : '-',
                }
        
        for i in range(count):
            data = datas[i]
            self.drawSingleBracket(data, x0 = x0, y0 = y0, w0=width, h0=height)
            y0 += offset

    def drawSingleBracket(self, data, x0=100, y0=100, w0=160, h0=30):
        """ draws a single branch and fills up with data """

        ''' Length Ratio Constants for the rectangles '''
        ID_LEN_RATIO = 0.2
        COUNTRY_LEN_RATIO = 0.6
        GOAL_LEN_RATIO = 0.1
        PENALTY_LEN_RATIO = 0.1
        
        qp = QtGui.QPainter()
        qp.begin(self)

        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setColor(QtGui.QColor(255, 255, 255, 155))
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setCapStyle(QtCore.Qt.RoundCap)

        qp.setPen(pen)
        
    
        idX = x0
        idY = y0
        idW = w0*ID_LEN_RATIO 
        idH = h0

        homeX = idX + idW
        homeY = y0
        homeW = w0 * COUNTRY_LEN_RATIO
        homeH = h0 / 2

        hGoalX = homeX + homeW
        hGoalY = y0
        hGoalW = w0 * GOAL_LEN_RATIO
        hGoalH = h0/2

        hPenaltyX = hGoalX + hGoalW
        hPenaltyY = y0
        hPenaltyW = w0 * PENALTY_LEN_RATIO
        hPenaltyH = h0/2
        
        visitorX = idX + idW
        visitorY = y0 + h0 / 2
        visitorW = w0 * COUNTRY_LEN_RATIO
        visitorH = h0 / 2

        vGoalX = visitorX + visitorW
        vGoalY = y0 + h0 / 2
        vGoalW = w0 * GOAL_LEN_RATIO
        vGoalH = h0/2

        vPenaltyX = vGoalX + vGoalW
        vPenaltyY = y0 + h0 / 2
        vPenaltyW = w0 * PENALTY_LEN_RATIO
        vPenaltyH = h0/2

        idRect = QtCore.QRect(idX, idY, idW, idH)
        homeRect = QtCore.QRect(homeX, homeY, homeW, homeH)
        hGoalRect = QtCore.QRect(hGoalX, hGoalY, hGoalW, hGoalH)
        hPenaltyRect = QtCore.QRect(hPenaltyX, hPenaltyY, hPenaltyW, hPenaltyH)

        visitorRect = QtCore.QRect(visitorX, visitorY, visitorW, visitorH)
        vGoalRect = QtCore.QRect(vGoalX, vGoalY, vGoalW, vGoalH)
        vPenaltyRect = QtCore.QRect(vPenaltyX, vPenaltyY, vPenaltyW, vPenaltyH)
        
        qp.drawRect(idRect)

        qp.drawRect(homeRect)
        qp.drawRect(hGoalRect)

        qp.drawRect(hPenaltyRect)
        

        
        qp.drawRect(visitorRect)
        qp.drawRect(vGoalRect)

        qp.drawRect(vPenaltyRect)

        pen.setColor(QtGui.QColor(255, 255, 255))
        qp.setFont(QtGui.QFont('Cambria', weight=2000))
        qp.setPen(pen)


        year, month, day = data['Date'].split('-')                  #splitting the date into year, month and day
        date = ('{}.{} {}').format(month, day, data['Time'])        #createing a formatted datetime for match date
        qp.drawText(idX, idY-2, date)                               #draws the datetime text as a header of the bracket
        
        qp.drawText(idRect, QtCore.Qt.AlignCenter, data['id'])

        qp.drawText(homeRect, QtCore.Qt.AlignCenter, data['Home'])
        qp.drawText(hGoalRect, QtCore.Qt.AlignCenter, data['H-Goal'])
        
                
        qp.drawText(visitorRect, QtCore.Qt.AlignCenter, data['Visitor'])
        qp.drawText(vGoalRect, QtCore.Qt.AlignCenter, data['V-Goal'])

        pen.setColor(QtGui.QColor(255, 162, 96))
        qp.setPen(pen)
        qp.drawText(hPenaltyRect, QtCore.Qt.AlignCenter, data['H-Pen'])
        qp.drawText(vPenaltyRect, QtCore.Qt.AlignCenter, data['V-Pen'])

        
        qp.end()

    def drawBranches(self, x0=50, y0=50, xOffset=250, yOffset=50, width=160, height=30, count=4):
        """ draws branches of the specified count to connect the brackets """
        for i in range(count):
            self.drawSingleBranch(x0, y0, xOffset, yOffset, width, height)
            y0 += 2*yOffset #two times the offset because a branch connects two brackets
    
    def drawSingleBranch(self, x0=50, y0=50, xOffset=250, yOffset=50, width=160, height=30):
        """ draws a single branch of 6 points """

        '''
    (x1;y1)   (x2;y2)
        o------o
               |
       (x5;y5) o----o (x6;y6)
               |
        o------o
    (x3;y3)  (x4;y4)
        '''
        
        qp = QtGui.QPainter()
        qp.begin(self)

        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(250, 255, 200, 180))
        pen.setWidth(2)
        pen.setJoinStyle(QtCore.Qt.SvgMiterJoin)
        pen.setCapStyle(QtCore.Qt.FlatCap)

        qp.setPen(pen)

        x1 = x0 + width
        y1 = y0 + height/2

        x2 = x1 + (xOffset-width)/2
        y2 = y1

        x3 = x0 + width
        y3 = y0 + yOffset + height/2

        x4 = x3 + (xOffset-width)/2
        y4 = y3
        
        x5 = x2
        y5 = y0 + height + (yOffset-height)/2

        x6 = x0 + xOffset
        y6 = y5

        P1 = QtCore.QPoint(x1, y1)
        P2 = QtCore.QPoint(x2, y2)
        P3 = QtCore.QPoint(x3, y3)
        P4 = QtCore.QPoint(x4, y4)
        P5 = QtCore.QPoint(x5, y5)
        P6 = QtCore.QPoint(x6, y6)

        qp.drawPolyline(P1, P2, P5, P6, P5, P4, P3)

        qp.end()

#************************************************************************************************************************************************************#
        
class BracketScreen(QtGui.QWidget):

    def __init__(self, parent=None):
        super(BracketScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):

        self.backBtn = QtGui.QPushButton('Back', self)
        self.backBtn.setObjectName('BackButton')
        
        brackets = BracketPainter(self)

        container = QtGui.QVBoxLayout()
        container.addWidget(brackets, 1)
        container.addWidget(self.backBtn, alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft)
        container.setSpacing(0)

        self.setLayout(container)

    def changeEvent(self, event):
        """ triggers retranslate ui when a language change occurs """
        super(BracketScreen, self).changeEvent(event)
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUI()

    def retranslateUI(self):
        """ retranslate all static texts that are listed below """
        self.backBtn.setText(self.tr('Back'))
#************************************************************************************************************************************************************#
