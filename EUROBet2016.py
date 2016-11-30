#!/usr/bin/python
#-*- coding: utf-8-*-

#eb2016.py

import sys
from PyQt4 import QtGui, QtCore

import pymssql
from sources.credentials import connString

import sources.shared as shared

from math import ceil

''' Source module imports '''

from sources.Dialogs import LoginDialog, AboutDialog
from sources.BetScreen import BetScreen, MatchScreen
from sources.GroupScreen import GroupScreen
from sources.BracketScreen import BracketScreen
from sources.ResultScreen import ResultScreen
from sources.ScoreScreen import ScoreScreen

#************************************************************************************************************************************************************#



class MainMenu(QtGui.QWidget):

    ################
    #   Signals    #
    ################
    
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)
        self.initUI()

    def initUI(self):
        
        ################
        # Controls     #
        ################
        self.betBtn = QtGui.QPushButton('Bets')
        self.groupBtn = QtGui.QPushButton('Groups')
        self.bracketBtn = QtGui.QPushButton('Elimination Rounds')
        self.resultBtn = QtGui.QPushButton('Match Result')
        self.scoreBtn = QtGui.QPushButton('Scores')

        ################
        # Widgets      #
        ################

        ################
        # Layout       #
        ################
        container = QtGui.QVBoxLayout()
        

        container.addWidget(self.betBtn)
        container.addWidget(self.groupBtn)
        container.addWidget(self.bracketBtn)
        container.addWidget(self.resultBtn)
        container.addWidget(self.scoreBtn)
        
        
        self.setLayout(container)

    def changeEvent(self, event):
        super(MainMenu, self).changeEvent(event)
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUI()

    def retranslateUI(self):
        self.betBtn.setText(self.tr('Bets'))
        self.groupBtn.setText(self.tr('Groups'))
        self.bracketBtn.setText(self.tr('Elimination Rounds'))
        self.resultBtn.setText(self.tr('Match results'))
        self.scoreBtn.setText(self.tr('Scores'))
        

#************************************************************************************************************************************************************#

class EUROBet2016(QtGui.QMainWindow):

    def __init__(self):
        super(EUROBet2016, self).__init__()
        self.initUI()

    def initUI(self):

        ################
        # Processes    #
        ################   
        self.panicProcess = QtCore.QProcess(self)
        self.updateProcess = QtCore.QProcess(self)
        
        ################
        # Translations #
        ################   
        ''' Init translation '''
        self.language = shared.getCfgLang()
        self.translator = QtCore.QTranslator()
        self.translator.load('resources/translations/%s.qm' % (self.language) )
        QtGui.qApp.installTranslator(self.translator)
    
        ################
        # Widgets      #
        ################   
        self.mainMenu = MainMenu(self)
        self.mainMenu.betBtn.clicked.connect(self.onToDates)
        self.mainMenu.groupBtn.clicked.connect(self.onToGroups)
        self.mainMenu.bracketBtn.clicked.connect(self.onToBrackets)
        self.mainMenu.resultBtn.clicked.connect(self.onToResults)
        self.mainMenu.scoreBtn.clicked.connect(self.onToScores)
        
        self.betDates = BetScreen(self)
        self.betDates.backBtn.clicked.connect(self.onToMain)
        self.betDates.toMatches.connect(self.onToMatchBets)
        self.matchBets = MatchScreen(self)
        self.matchBets.backBtn.clicked.connect(self.onToDates)
        
        self.groups = GroupScreen(self)
        self.groups.backBtn.clicked.connect(self.onToMain)

        self.brackets = BracketScreen(self)
        self.brackets.backBtn.clicked.connect(self.onToMain)

        self.results = ResultScreen(self)
        self.results.backBtn.clicked.connect(self.onToMain)

        self.scores = ScoreScreen(self)
        self.scores.backBtn.clicked.connect(self.onToMain)
        
        
        ################
        # Layouts      #
        ################
        
        self.mainWidget = QtGui.QStackedWidget(self)
        self.mainWidget.addWidget(self.mainMenu)
        self.mainWidget.addWidget(self.betDates)
        self.mainWidget.addWidget(self.matchBets)
        self.mainWidget.addWidget(self.results)
        self.mainWidget.addWidget(self.groups)
        self.mainWidget.addWidget(self.brackets)
        self.mainWidget.addWidget(self.scores)
        self.mainWidget.setCurrentWidget(self.mainMenu)
        
        ################
        # Actions      #
        ################
        self.exitAction = QtGui.QAction(self)
        self.exitAction.setIcon(QtGui.QIcon('resources/icons/exit.png'))
        self.exitAction.setShortcut('Ctrl+X')
        self.exitAction.triggered.connect(QtGui.qApp.quit)

        self.aboutAction = QtGui.QAction(self)
        self.aboutAction.setIcon(QtGui.QIcon('resources/icons/about.png'))
        self.aboutAction.triggered.connect(self.showAboutDialog)

        self.logoutAction = QtGui.QAction(self)
        self.logoutAction.setIcon(QtGui.QIcon('resources/icons/logout.png'))
        self.logoutAction.triggered.connect(self.onLogout)

        self.refreshAction = QtGui.QAction(self)
        self.refreshAction.setIcon(QtGui.QIcon('resources/icons/refresh.png'))
        self.refreshAction.setShortcut('F5')
        self.refreshAction.triggered.connect(self.onRefresh)        

        self.langSwitchAction = QtGui.QAction(self)
        self.langSwitchAction.setIcon(QtGui.QIcon('resources/icons/%s.png' % (self.language)))
        self.langSwitchAction.triggered.connect(self.onLangSwitch)
      
        
        ################
        #   Menus      #
        ################
        self.statusBar()   

        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.setIconSize(QtCore.QSize(36, 36))
        self.toolbar.setMovable(False)
        
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.logoutAction)
        self.toolbar.addAction(self.refreshAction)
        self.toolbar.addAction(self.aboutAction)
        
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.langSwitchAction)
        
        ##########################
        # Window settings        #
        ##########################
        self.retranslateUI()

        self.versionString = shared.getCfgVersionString()

        self.setCentralWidget(self.mainWidget)
        self.setWindowTitle('EURO Bet 2016 ' + self.versionString)
        self.setWindowIcon(QtGui.QIcon('resources/icons/euro.png'))

        self.setFixedSize(1024, 530)

        self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon('resources/icons/euro.png'))
        self.trayIcon.activated.connect(self.restoreWindow)
        
        self.show()

        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.setSingleShot(True)
        self.updateTimer.setInterval(1000)
        self.updateTimer.timeout.connect(self.checkUpdate)
        self.updateTimer.start()

    ##########################
    # Slots                  #
    ##########################
    
    def onToMain(self):
        self.mainWidget.setCurrentWidget(self.mainMenu)

    def onToMatchBets(self, date):
        date = str(date)
        self.matchBets.reinitUI(date)
        self.mainWidget.setCurrentWidget(self.matchBets)
        
    def onToDates(self):
        self.mainWidget.setCurrentWidget(self.betDates)

    def onToResults(self):
        self.results.reinitUI()
        self.mainWidget.setCurrentWidget(self.results)
        
    def onToGroups(self):
        self.mainWidget.setCurrentWidget(self.groups)

    def onToBrackets(self):
        self.mainWidget.setCurrentWidget(self.brackets)

    def onToScores(self):
        self.scores.reinitUI()
        self.mainWidget.setCurrentWidget(self.scores)

    ##########################
    # Methods                #
    ##########################   
        
    def showAboutDialog(self):
        about = AboutDialog()

    def onLogout(self):
        """ Closing mainwindow, exit from application, reset USERNAME """
        self.close()
        self.deleteLater()
        QtGui.qApp.removeTranslator(self.translator)
        QtCore.QCoreApplication.instance().exit(1)

    def onRefresh(self):
        """ Refreshes application by reloading dynamic widgets """
        self.results.reinitUI()
        self.scores.reinitUI()

    def onLangSwitch(self):
        """ Switch language during runtime """
        langs = shared.getTranslatedLangsFromDir() # get available translation languages

        actIndex = langs.index(self.language)

        if actIndex == len(langs) - 1:
            actIndex = 0
        else:
            actIndex += 1

        self.language = langs[actIndex]
        self.translator.load('resources/translations/%s.qm' % (self.language))
        self.langSwitchAction.setIcon(QtGui.QIcon('resources/icons/%s.png' % (self.language)))
        shared.setCfgLang(self.language)
        
        QtGui.qApp.installTranslator(self.translator)
        
        self.retranslateUI()


    def retranslateUI(self):
        """ collects every static string that should be translated"""
        self.exitAction.setText(self.tr('Exit'))
        self.exitAction.setStatusTip(self.tr('Exit application'))
        self.aboutAction.setText(self.tr('About'))
        self.aboutAction.setStatusTip(self.tr('About'))
        self.logoutAction.setText(self.tr('Logout'))
        self.logoutAction.setStatusTip(self.tr('Logout'))
        self.refreshAction.setText(self.tr('Refresh'))
        self.refreshAction.setStatusTip(self.tr('Refresh'))
        self.langSwitchAction.setText(self.tr('Language switch'))
        self.langSwitchAction.setStatusTip(self.tr('Switch Language'))

    def keyPressEvent(self, event):
        
        print event.key()
        print event.modifiers().__int__()
        if event.modifiers().__int__() == QtCore.Qt.CTRL:
            ''' watching for CTRL modifier '''
            if event.key() == (QtCore.Qt.Key_Q):
                ''' if CTRL + Q pressed then start panic process, hides the app,
                    starts notepad and shows the tray icon '''
                self.panicProcess.start("notepad")
                self.hide()
                self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.Tool)
                self.trayIcon.show()
    
        if event.key() == (QtCore.Qt.Key_Escape):
            ''' watching for escape pressed, and if the current widget has a back button
                triggers its click function '''
            try:
                self.mainWidget.currentWidget().backBtn.click()
            except:
                pass
        elif event.key() == (QtCore.Qt.Key_Return):
            ''' watching for return pressed, and if the current widget has a submit button
                triggers its click function '''
            try:
                self.mainWidget.currentWidget().submitBtn.click()
            except:
                pass
        elif event.key() == QtCore.Qt.Key_Left:
            print 'Leftarrow'
            try:
                pagerBtns = self.mainWidget.currentWidget().resultPager.btnGroup.buttons()
                checkedBtn = self.mainWidget.currentWidget().resultPager.btnGroup.checkedButton()

                page = pagerBtns.index(checkedBtn)
            
                if page > 0:
                    pagerBtns[page-1].click()
                    
            except:
                pass
            
        elif event.key() == QtCore.Qt.Key_Right:
            print 'Rightarrow'
            try:
                pagerBtns = self.mainWidget.currentWidget().resultPager.btnGroup.buttons()
                checkedBtn = self.mainWidget.currentWidget().resultPager.btnGroup.checkedButton()

                page = pagerBtns.index(checkedBtn)
                
                if page < len(pagerBtns) - 1:
                    pagerBtns[page+1].click()
            except:
                pass
            
    def restoreWindow(self, reason):
        """ restores main window if the tray icon is double clicked"""
        if reason == QtGui.QSystemTrayIcon.DoubleClick:
            self.trayIcon.hide()
            self.showNormal()

    def checkUpdate(self):
        """ checks for update """
        if shared.checkUpdateServerAvailable():
            actual = self.versionString
            newest = shared.getNewestVersionString()

            actualVal = shared.getVersionStringValue(actual)
            newestVal = shared.getVersionStringValue(newest)
            
            print actualVal, newestVal
            if newestVal > actualVal:
                updateMsg = self.tr("Newer version of EURO Bet 2016 found!\nDo you want to update now?")
                reply = QtGui.QMessageBox.question(self, self.tr("Update found"),
                                                   updateMsg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    self.updateProcess.startDetached(r'EUROBet2016_Updater.exe -u')
                    QtGui.qApp.quit()
                    
        else:
            print 'no update yet'
        

#************************************************************************************************************************************************************#

def main(app = QtGui.QApplication(sys.argv)):
    """ app is an input parameter for main,
        to be able to call it recursively, after logouts"""
    
    with open('resources/styles/default.css', 'r') as appStyle:
            app.setStyleSheet(appStyle.read())
    
    """ Login screen """
    login = LoginDialog()

    if login.exec_() == QtGui.QDialog.Accepted:
        """ Successful login """
        """ Start GUI """
        gui = EUROBet2016()

        """ Save application return code on exit """
        appReturnCode = app.exec_()    
        if appReturnCode == 0:
            """ Normal Quit from application """
            sys.exit()
        elif appReturnCode == 1:
            """ Logout from application, restart main method with
                the instance of the current app """
            main(app)    
    else:
        """ Exit from login screen """
        sys.exit()

if __name__ == '__main__':
    main()
