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

''' Inbuilt imports '''
from math import ceil
import datetime
#************************************************************************************************************************************************************#


class BettingDialog(QtGui.QDialog):

 

    def __init__(self, parent=None):
        super(BettingDialog, self).__init__(parent)
        self.initUI()

    def initUI(self):

        self.form = QtGui.QFormLayout()
        self.setLayout(self.form)
        self.setWindowTitle(self.tr('Bets'))
        self.setWindowIcon(QtGui.QIcon('resources/icons/euro.png'))

        self.closeTimer = QtCore.QTimer(self)
        self.closeTimer.setSingleShot(True)
        self.closeTimer.setInterval(1250)
        self.closeTimer.timeout.connect(self.close)

##        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)

    def enterEvent(self, event):
        super(BettingDialog, self).enterEvent(event)
        self.closeTimer.stop()
    def leaveEvent(self, event):
        super(BettingDialog, self).leaveEvent(event)
        self.closeTimer.start()

        
#************************************************************************************************************************************************************#
class BetValue(QtGui.QLineEdit):

    def __init__(self, parent=None):
        super(BetValue, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.oldText = ''
        self.setInputMask("99; ")
        self.setMaximumWidth(50)
        self.setPlaceholderText(" -")
        self.setMaxLength(2)

    def mousePressEvent(self, event):
        super(BetValue, self).mousePressEvent(event)
        self.oldText = self.text()
        self.setText('')
        self.setCursorPosition(0)

    def keyPressEvent(self, event):
        super(BetValue, self).keyPressEvent(event)
        ''' The current text is copied and shifted by one space to the left
            after the first character entered '''
        print len(self.text())
        if len(self.text()) == 1:
            self.setText(self.text() + ' ')
            self.setCursorPosition(1)
            

    def focusOutEvent(self, event):
        super(BetValue, self).focusOutEvent(event)
        ''' When there is no change to the widget, the current text is
            replaced by the previous '''
        if (self.text() == ''):
            self.setText(self.oldText)
        print len(self.text())
        if len(self.text()) == 1:
            print self.text()
            self.setText(' ' + self.text())
            
        
#************************************************************************************************************************************************************#
        
class BetEntry(QtGui.QWidget):

    def __init__(self, parent=None):
        super(BetEntry, self).__init__(parent)
        self.initUI()
        
    def initUI(self):

        self.lastToolTipPos = None

        self.matchId = 0
        self.matchDate = datetime.datetime.now()
    
        self.homeBtn = QtGui.QPushButton("Home")
        self.homeBtn.setIcon(QtGui.QIcon('resources/flags/default.png'))
        self.homeBtn.setObjectName('HomeTeam')

        self.homeTxt = BetValue(self)
    
        self.visitorBtn = QtGui.QPushButton("Visitor")
        self.visitorBtn.setIcon(QtGui.QIcon('resources/flags/default.png'))
        self.visitorBtn.setObjectName('VisitorTeam')
    
        self.visitorTxt = BetValue(self)

        colon = QtGui.QLabel(':')
        colon.setMaximumWidth(20)

        container = QtGui.QGridLayout()
        container.addWidget(self.homeBtn, 0, 0)
        container.addWidget(self.homeTxt, 0, 1)
        container.addWidget(colon, 0, 2)
        container.addWidget(self.visitorTxt, 0, 3)
        container.addWidget(self.visitorBtn, 0, 4)
     
        self.setLayout(container)

        self.countdownTimer = QtCore.QTimer()
        self.countdownTimer.setInterval(1000)
        self.countdownTimer.start()
        self.countdownTimer.timeout.connect(self.setCountdownTime)
        
    def setMatchId(self, ID):
        """ sets the matchId to the specified ID """
        self.matchId = ID

    def createDateTuple(self, date):
        """ returns a list of integers containing the year, month, day of the date string """
        return [int(i) for i in date.split('-')]
    
    def createTimeTuple(self, time):
        """ returns a list of integers containing the hour and minute of the time string """

        ''' extending the time to get the format of hh:mm:ss '''
        time += ':00'
        
        return [int(i) for i in time.split(':')]

    def createDatetimeTuple(self, date, time):
        """ joins the date and the time tuple """
        d = self.createDateTuple(date)
        t = self.createTimeTuple(time)
        dt = []
        ''' [yyyy, mm, dd] '''
        dt.extend(d)
        ''' [yyyy, mm, dd, hh, mm, ss] '''
        dt.extend(t) 
        return dt
    
    def setMatchDate(self, date, time):
        """ sets the matchDate variable to the provided date and time """
        dt = self.createDatetimeTuple(date, time)
        date = datetime.datetime(*dt)
        self.matchDate = date.replace(hour=date.hour-1) # decrementing the starting hour by 1 to get the bet closing date
        

    def createCountdownTime(self):
        """ returns countdown time to matchdate """
        diff = self.matchDate - datetime.datetime.now()

        days = diff.days
        hours = diff.seconds/3600
        mins = diff.seconds/60 - hours*60
        secs = diff.seconds - mins*60 - hours*3600

        print "{}n {}o {}p {}s".format(days, hours, mins, secs)
        return {
                'd' : days,
                'h' : hours,
                'm' : mins,
                's' : secs
                }
        
    def setCountdownTime(self):
        """ sets the timeLbl's text to the specified time """
        cd = self.createCountdownTime()
        if cd['d'] < 0:
            self.countdownTimer.stop()
        else:
            tooltip = self.tr("Betting ends in: {}d {:0>2}:{:0>2}:{:0>2}".format(cd['d'], cd['h'], cd['m'], cd['s'])) if cd['d'] else \
                          self.tr("Betting ends in: {:0>2}:{:0>2}:{:0>2}".format(cd['h'], cd['m'], cd['s']))          if cd['h'] else \
                                 self.tr("Betting ends in: {:0>2}:{:0>2}".format(cd['m'], cd['s']))                   if cd['m'] else \
                                        self.tr("Betting ends in: {:0>2}".format(cd['s']))
        
        if self.lastToolTipPos:
            QtGui.QToolTip.hideText()
            QtGui.QToolTip.showText(self.lastToolTipPos, tooltip)
    
    def setHomeBtnText(self, country):
        self.homeBtn.setText(country)
        icon = shared.getCountryFlagPath(country)
        self.homeBtn.setIcon(QtGui.QIcon(icon))

    def getHomeBtnText(self):
        return self.homeBtn.text()
        
    def setVisitorBtnText(self, country):
        self.visitorBtn.setText(country)
        icon = shared.getCountryFlagPath(country)
        self.visitorBtn.setIcon(QtGui.QIcon(icon))

    def getVisitorBtnText(self):
        return self.visitorBtn.text()

    def setHomeGoals(self, goals):
        self.homeTxt.setText(str(goals))

    def getHomeGoals(self):
        return int(self.homeTxt.text())

    def setVisitorGoals(self, goals):
        self.visitorTxt.setText(str(goals))

    def getVisitorGoals(self):
        return int(self.visitorTxt.text())

    def event(self, event):
        """ creating dynamic tooltip display """
        super(BetEntry, self).event(event)
        if event.type() == QtCore.QEvent.ToolTip:
            self.lastToolTipPos = event.globalPos()
        elif event.type() == QtCore.QEvent.Leave:
            self.lastToolTipPos = None
            QtGui.QToolTip.hideText()
        return True
        
#************************************************************************************************************************************************************#
        
class MatchScreen(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(MatchScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):

        self.date = '06.11'
        
        self.backBtn = QtGui.QPushButton('Back')
        self.backBtn.setObjectName('BackButton')
        self.backBtn.clicked.connect(self.haltCountdownTimers)

        self.submitBtn = QtGui.QPushButton('Submit')
        self.submitBtn.setObjectName('SubmitButton')
        self.submitBtn.setMaximumWidth(200)
        self.submitBtn.clicked.connect(self.submitBets)

        self.header = QtGui.QLabel('06.10')
        self.header.setMaximumHeight(50)
        
        self.matchEntries = self.createMatchEntries()   # to contain bet entry instances 
        
        
        self.matchContainer = QtGui.QVBoxLayout()
        self.setMatchContainer()
        
        btnContainer = QtGui.QHBoxLayout()
        btnContainer.addWidget(self.backBtn, alignment=QtCore.Qt.AlignLeft)
        btnContainer.addWidget(self.submitBtn, alignment=QtCore.Qt.AlignRight)
        btnContainer.setAlignment(QtCore.Qt.AlignBottom)
        
        self.container = QtGui.QVBoxLayout(self)
        self.container.addWidget(self.header)
        self.container.setAlignment(self.header, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.container.addLayout(self.matchContainer)
        self.container.addLayout(btnContainer)
        self.container.setAlignment(btnContainer, QtCore.Qt.AlignBottom)
        self.setLayout(self.container)

    def splitDate(self, date):
        """ splits the date of format 'mm.dd' into a separate
            month 'mm' and day 'dd' """
        month = date.split('.')[0]
        day = date.split('.')[1]
        return (month, day)

    def getMatchBetsForDate(self):
        """ fetches and returns every match bet that is being held
            on the given date """
        matches = []
        username = shared.getCfgUsername()
        month, day = self.splitDate(self.date)
        lang = shared.getCfgCountryCode()

        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor(as_dict=True)
                cur.callproc('eb_2016_get_bet', (username, month, day, lang,))
        
                for row in cur:
                    matches.append({'id'     : row['ID'],
                                    'Date'   : row['Date'],
                                    'Time'   : row['Time'],
                                    'Home'   : row['Home'],
                                    'H-Goal' : row['H-Goal'],
                                    'Visitor': row['Visitor'],
                                    'V-Goal' : row['V-Goal']})
        except:
            QtGui.QMessageBox.about(self, self.tr('Database connection fault'), self.tr('Failed to connect to database.\nPlease try again later'))
            QtGui.qApp.quit()
            
        return matches

    def createMatchEntries(self):
        """ creates match entries from matches """
        matches = self.getMatchBetsForDate()
        matchEntries = []
        for match in matches:
            entry = BetEntry(self)
            entry.setMatchId(match['id'])
            entry.setMatchDate(match['Date'], match['Time'])
            entry.setHomeBtnText(match['Home'])
            entry.setHomeGoals(match['H-Goal'])
            entry.setVisitorBtnText(match['Visitor'])
            entry.setVisitorGoals(match['V-Goal'])
            matchEntries.append(entry)
        return matchEntries


    def clearMatchEntries(self):
        """ removes every versus widget from the match container
            then deletes them, and empties the matches array """
        for entry in self.matchEntries:
            self.matchContainer.removeWidget(entry)
            entry.setParent(None)
            entry.deleteLater()
            entry.countdownTimer.stop()
        self.matchEntries = []

    def setMatchContainer(self):
        """ populates the match container with match entries"""
        for entry in self.matchEntries:
            self.matchContainer.addWidget(entry)

    def submitBets(self):
        """ iterates through every versus widget, and if there's valid entry
            submits it to the database """
        username = shared.getCfgUsername()
        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor()

                response = ''
                bettingDialog = BettingDialog()
                lbl1 = QtGui.QLabel()
                lbl2 = QtGui.QLabel()
                
                for match in self.matchEntries:

                    matchId = match.matchId
                    home = match.getHomeBtnText()
                    visitor = match.getVisitorBtnText()
                    lbl1 = QtGui.QLabel()
                    lbl2 = QtGui.QLabel()
                    
                    
                    try:
                        homeGoals = match.getHomeGoals()
                        visitorGoals = match.getVisitorGoals()
                        cur.callproc('eb_2016_match_bet', (username, matchId, homeGoals, visitorGoals,))
                        if cur.returnvalue == 0:
                            ''' successful bet within deadline '''
                            lbl1.setText(home + ' - ' + visitor + ':')
                            lbl2.setText(self.tr('bet submitted'))
                            lbl2.setObjectName('OkLabel')
                            bettingDialog.form.addRow(lbl1, lbl2) 

                    except ValueError:
                        cur.callproc('eb_2016_match_bet', (username, matchId, None, None))
                        if cur.returnvalue == 0:
                            ''' successful bet within deadline '''
                            lbl1.setText(home + ' - ' + visitor + ':')
                            lbl2.setText(self.tr('bet missing'))
                            lbl2.setObjectName('NokLabel')
                            bettingDialog.form.addRow(lbl1, lbl2) 

                            
                    if cur.returnvalue == 1:
                        ''' betting period is over, deadline met '''
                        lbl1.setText(home + ' - ' + visitor + ':')
                        lbl2.setText(self.tr('betting is over'))
                        lbl2.setObjectName('NokLabel')
                        bettingDialog.form.addRow(lbl1, lbl2)

                                                
                    conn.commit()   #must be committed to run the procedure

            bettingDialog.closeTimer.start()
            bettingDialog.exec_()
            
            
        except:
            print sys.exc_info()
            QtGui.QMessageBox.about(self, self.tr('Database connection fault'), self.tr('Failed to connect to database.\nPlease try again later'))
            QtGui.qApp.quit()

    def checkBetDeadline(self):
        """ iterates through every match entry, sends the match id, and based on the
            return value of the server - in case of an expired betting session - disables
            bet value field """

        try:
            conn = pymssql.connect(*connString)
            with conn:
                

                cur = conn.cursor()

                for match in self.matchEntries:
                    matchId = match.matchId
                    
                    cur.callproc('eb_2016_can_i_bet', (matchId,))
                    conn.commit()

                    if cur.returnvalue == 0:
                        print '{}: ongoing'.format(matchId)
                    elif cur.returnvalue == 1:
                        match.homeTxt.setDisabled(True)
                        match.visitorTxt.setDisabled(True)
                
        except:
            print sys.exc_info()
            QtGui.QMessageBox.about(self, self.tr('Database connection fault'), self.tr('Failed to connect to database.\nPlease try again later'))
            QtGui.qApp.quit()

    def haltCountdownTimers(self):
        """ stops countdown timers of the current bet entries """
        for entry in self.matchEntries:
            entry.countdownTimer.stop()
        

    def reinitUI(self, date):
        """ reinitialize UI, sets date, clears match entries and match container,
            recreates match entries, reloads match container """
        self.date = date
        self.header.setText(date)
        self.clearMatchEntries()
        self.matchEntries = self.createMatchEntries()
        print self.matchEntries
        self.checkBetDeadline()
        self.setMatchContainer()

    def changeEvent(self, event):
        """ triggers retranslate ui when a language change occurs """
        super(MatchScreen, self).changeEvent(event)
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUI()

    def retranslateUI(self):
        """ retranslate all static texts that are listed below """
        self.reinitUI(self.date)
        self.backBtn.setText(self.tr('Back'))
        self.submitBtn.setText(self.tr('Submit'))            
   
#************************************************************************************************************************************************************#
        
class BetScreen(QtGui.QWidget):
    
    toMatches = QtCore.pyqtSignal(str, name='toMatches')
    
    def __init__(self, parent=None):
        super(BetScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.backBtn = QtGui.QPushButton('Back')
        self.backBtn.setObjectName('BackButton')
        
        self.dates = self.getDates() #list that will contain date of matches
        
                
        self.dateContainer = QtGui.QGridLayout()
        self.setDateContainer(cols=4)

        container = QtGui.QVBoxLayout()
        container.addLayout(self.dateContainer)
        container.addWidget(self.backBtn, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.setLayout(container)

    def getDates(self):
        """ fetches and returns match dates in the format of mm.dd """
        conn = pymssql.connect(*connString)
        cur = conn.cursor(as_dict=True) #as_dict to access row element by column name
        try:
            cur.execute('SELECT [Date] FROM [dbo].[EB_2016_matches]')
            matchDates = []
            for row in cur:
                #formatting the date, original format: yyyy-mm-dd, needed format mm.dd
                trimDate = str(row['Date'].split('-')[1]) + '.' + str(row['Date'].split('-')[2])
                if trimDate not in matchDates:
                    matchDates.append(trimDate)

            return matchDates
        except:
            msg = "Couldn't connect to database"
            print 'Database fault'
            
        conn.close()

    def setDateContainer(self, cols=4):
        """ creates buttons with the corresponding date text """
        rows = int(ceil(float(len(self.dates)) / cols)) # calculates the number of needed rows

        positions = [(row, col) for row in range(rows) for col in range(cols)] # creates an array of (row, col) coordinates for the grid layout
        
        for date, position in zip(self.dates, positions): # creates the date picking buttons and add them to the container layout
            btn = QtGui.QPushButton(date)
            btn.setMaximumWidth(150)
            btn.clicked.connect(self.onDatePick)
            self.dateContainer.addWidget(btn, *position)
        
    def onDatePick(self):
        """ triggers toMatches signal, with the text of the clicked button """
        self.toMatches.emit(str(self.sender().text()))

    def changeEvent(self, event):
        """ triggers retranslate ui when a language change occurs """
        super(BetScreen, self).changeEvent(event)
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUI()

    def retranslateUI(self):
        """ retranslate all static texts that is listed below """
        self.backBtn.setText(self.tr('Back'))

#************************************************************************************************************************************************************#
